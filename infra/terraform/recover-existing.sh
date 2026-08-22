#!/usr/bin/env bash
set -euo pipefail

NAME="vitapoint-production"
REGION="${AWS_REGION:-sa-east-1}"

has_state() { terraform state list 2>/dev/null | grep -qx "$1"; }
import_if() {
  local address="$1" id="$2"
  [ -z "$id" ] && return 0
  has_state "$address" && return 0
  echo "Importing $address -> $id"
  terraform import "$address" "$id" || true
}

VPC_ID=$(aws ec2 describe-vpcs --region "$REGION" --filters "Name=tag:Name,Values=${NAME}-vpc" --query 'Vpcs[0].VpcId' --output text 2>/dev/null || true)
[ "$VPC_ID" = "None" ] && VPC_ID=""
import_if aws_vpc.main "$VPC_ID"

if [ -n "$VPC_ID" ]; then
  IGW_ID=$(aws ec2 describe-internet-gateways --region "$REGION" --filters "Name=attachment.vpc-id,Values=$VPC_ID" --query 'InternetGateways[0].InternetGatewayId' --output text 2>/dev/null || true)
  [ "$IGW_ID" = "None" ] && IGW_ID=""
  import_if aws_internet_gateway.main "$IGW_ID"

  for i in 0 1; do
    n=$((i+1))
    PUB=$(aws ec2 describe-subnets --region "$REGION" --filters "Name=vpc-id,Values=$VPC_ID" "Name=tag:Name,Values=${NAME}-public-${n}" --query 'Subnets[0].SubnetId' --output text 2>/dev/null || true)
    PRIV=$(aws ec2 describe-subnets --region "$REGION" --filters "Name=vpc-id,Values=$VPC_ID" "Name=tag:Name,Values=${NAME}-private-${n}" --query 'Subnets[0].SubnetId' --output text 2>/dev/null || true)
    [ "$PUB" = "None" ] && PUB=""; [ "$PRIV" = "None" ] && PRIV=""
    import_if "aws_subnet.public[$i]" "$PUB"
    import_if "aws_subnet.private[$i]" "$PRIV"
  done

  RT_ID=$(aws ec2 describe-route-tables --region "$REGION" --filters "Name=vpc-id,Values=$VPC_ID" --query "RouteTables[?Routes[?GatewayId=='${IGW_ID}']].RouteTableId | [0]" --output text 2>/dev/null || true)
  [ "$RT_ID" = "None" ] && RT_ID=""
  import_if aws_route_table.public "$RT_ID"
  if [ -n "$RT_ID" ]; then
    for i in 0 1; do
      n=$((i+1))
      PUB=$(aws ec2 describe-subnets --region "$REGION" --filters "Name=vpc-id,Values=$VPC_ID" "Name=tag:Name,Values=${NAME}-public-${n}" --query 'Subnets[0].SubnetId' --output text 2>/dev/null || true)
      ASSOC=$(aws ec2 describe-route-tables --region "$REGION" --route-table-ids "$RT_ID" --query "RouteTables[0].Associations[?SubnetId=='${PUB}'].RouteTableAssociationId | [0]" --output text 2>/dev/null || true)
      [ "$ASSOC" = "None" ] && ASSOC=""
      import_if "aws_route_table_association.public[$i]" "$ASSOC"
    done
  fi

  for kind in alb api db; do
    SG=$(aws ec2 describe-security-groups --region "$REGION" --filters "Name=vpc-id,Values=$VPC_ID" "Name=group-name,Values=${NAME}-${kind}" --query 'SecurityGroups[0].GroupId' --output text 2>/dev/null || true)
    [ "$SG" = "None" ] && SG=""
    import_if "aws_security_group.${kind}" "$SG"
  done
fi

import_if aws_ecr_repository.api "$(aws ecr describe-repositories --region "$REGION" --repository-names ${NAME}-api --query 'repositories[0].repositoryName' --output text 2>/dev/null || true)"
import_if aws_cloudwatch_log_group.api "/ecs/${NAME}-api"
import_if aws_ecs_cluster.main "${NAME}-cluster"
import_if aws_db_subnet_group.main "$(aws rds describe-db-subnet-groups --region "$REGION" --db-subnet-group-name ${NAME}-db --query 'DBSubnetGroups[0].DBSubnetGroupName' --output text 2>/dev/null || true)"
import_if aws_db_instance.main "$(aws rds describe-db-instances --region "$REGION" --db-instance-identifier ${NAME}-postgres --query 'DBInstances[0].DBInstanceIdentifier' --output text 2>/dev/null || true)"

SECRET_ARN=$(aws secretsmanager describe-secret --region "$REGION" --secret-id "${NAME}/api" --query ARN --output text 2>/dev/null || true)
[ "$SECRET_ARN" = "None" ] && SECRET_ARN=""
import_if aws_secretsmanager_secret.api "$SECRET_ARN"

for role in ecs-execution ecs-task github-deploy; do
  ROLE_NAME="${NAME}-${role}"
  if aws iam get-role --role-name "$ROLE_NAME" >/dev/null 2>&1; then
    case "$role" in
      ecs-execution) import_if aws_iam_role.task_execution "$ROLE_NAME" ;;
      ecs-task) import_if aws_iam_role.task "$ROLE_NAME" ;;
      github-deploy) import_if aws_iam_role.github_deploy "$ROLE_NAME" ;;
    esac
  fi
done

echo "Recovery import completed."

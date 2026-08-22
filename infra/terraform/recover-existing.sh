#!/usr/bin/env bash
set -euo pipefail

NAME="vitapoint-production"
REGION="${AWS_REGION:-sa-east-1}"

has_state() { terraform state list 2>/dev/null | grep -qx "$1"; }
import_if() {
  local address="$1" id="$2"
  [ -z "$id" ] && return 0
  [ "$id" = "None" ] && return 0
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

ECR_NAME=$(aws ecr describe-repositories --region "$REGION" --repository-names ${NAME}-api --query 'repositories[0].repositoryName' --output text 2>/dev/null || true)
import_if aws_ecr_repository.api "$ECR_NAME"

if aws logs describe-log-groups --region "$REGION" --log-group-name-prefix "/ecs/${NAME}-api" --query "logGroups[?logGroupName=='/ecs/${NAME}-api'].logGroupName | [0]" --output text 2>/dev/null | grep -qx "/ecs/${NAME}-api"; then
  import_if aws_cloudwatch_log_group.api "/ecs/${NAME}-api"
fi

CLUSTER_ARN=$(aws ecs describe-clusters --region "$REGION" --clusters "${NAME}-cluster" --query 'clusters[0].clusterArn' --output text 2>/dev/null || true)
import_if aws_ecs_cluster.main "$CLUSTER_ARN"

DB_SUBNET=$(aws rds describe-db-subnet-groups --region "$REGION" --db-subnet-group-name ${NAME}-db --query 'DBSubnetGroups[0].DBSubnetGroupName' --output text 2>/dev/null || true)
import_if aws_db_subnet_group.main "$DB_SUBNET"
DB_INSTANCE=$(aws rds describe-db-instances --region "$REGION" --db-instance-identifier ${NAME}-postgres --query 'DBInstances[0].DBInstanceIdentifier' --output text 2>/dev/null || true)
import_if aws_db_instance.main "$DB_INSTANCE"

SECRET_ARN=$(aws secretsmanager describe-secret --region "$REGION" --secret-id "${NAME}/api" --query ARN --output text 2>/dev/null || true)
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

LB_ARN=$(aws elbv2 describe-load-balancers --region "$REGION" --names "${NAME}-alb" --query 'LoadBalancers[0].LoadBalancerArn' --output text 2>/dev/null || true)
import_if aws_lb.api "$LB_ARN"

TG_ARN=$(aws elbv2 describe-target-groups --region "$REGION" --names "${NAME}-api" --query 'TargetGroups[0].TargetGroupArn' --output text 2>/dev/null || true)
import_if aws_lb_target_group.api "$TG_ARN"

if [ -n "$LB_ARN" ] && [ "$LB_ARN" != "None" ]; then
  LISTENER_ARN=$(aws elbv2 describe-listeners --region "$REGION" --load-balancer-arn "$LB_ARN" --query 'Listeners[?Port==`80`].ListenerArn | [0]' --output text 2>/dev/null || true)
  import_if aws_lb_listener.http "$LISTENER_ARN"
fi

TASK_DEF_ARN=$(aws ecs describe-task-definition --region "$REGION" --task-definition "${NAME}-api" --query 'taskDefinition.taskDefinitionArn' --output text 2>/dev/null || true)
import_if aws_ecs_task_definition.api "$TASK_DEF_ARN"

SERVICE_ARN=$(aws ecs describe-services --region "$REGION" --cluster "${NAME}-cluster" --services "${NAME}-api" --query 'services[0].serviceArn' --output text 2>/dev/null || true)
if [ -n "$SERVICE_ARN" ] && [ "$SERVICE_ARN" != "None" ]; then
  import_if aws_ecs_service.api "${NAME}-cluster/${NAME}-api"
fi

echo "Recovery import completed."

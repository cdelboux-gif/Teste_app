import { router, useFocusEffect } from 'expo-router';
import { useCallback, useState } from 'react';
import { ActivityIndicator, Pressable, ScrollView, StyleSheet, Text, View } from 'react-native';

import { apiRequest } from '../src/api';
import { getAccessToken } from '../src/auth';

type Home = {
  user: { first_name: string | null; onboarding_completed: boolean };
  health_score: { score: number | null; status: string; component_count: number };
  checkin: { completed_today: boolean; today: null | { mood:number; anxiety:number; energy:number; stress:number; sleep_quality:number } };
  trend_7d: { days_with_data:number; averages:null | { mood:number; anxiety:number; energy:number; stress:number; sleep_quality:number } };
  recommended_trail: { code:string; name:string; description:string };
  next_actions: { type:string; title:string; priority:number }[];
};

const Card=({title,value,caption}:{title:string,value:string,caption:string})=><View style={s.card}><Text style={s.cardTitle}>{title}</Text><Text style={s.value}>{value}</Text><Text style={s.caption}>{caption}</Text></View>;
const statusLabel=(x:string)=>({stable:'Estável',attention:'Atenção',needs_attention:'Requer atenção',baseline_pending:'Linha de base pendente'}[x]??x);

export default function Dashboard(){
  const [data,setData]=useState<Home|null>(null); const [error,setError]=useState(''); const [loading,setLoading]=useState(true);
  const load=useCallback(async()=>{setLoading(true);setError('');try{const token=await getAccessToken();if(!token){router.replace('/login');return;}const home=await apiRequest<Home>('/dashboard/home',{},token);setData(home);}catch(e){setError(e instanceof Error?e.message:'Não foi possível carregar o painel.');}finally{setLoading(false);}},[]);
  useFocusEffect(useCallback(()=>{void load();},[load]));
  if(loading&&!data)return <View style={s.center}><ActivityIndicator size="large"/><Text style={s.caption}>Carregando seu painel…</Text></View>;
  const score=data?.health_score.score; const avg=data?.trend_7d.averages;
  return <ScrollView style={s.page} contentContainerStyle={s.content}>
    <Text style={s.hello}>Olá{data?.user.first_name?`, ${data.user.first_name}`:''} 👋</Text><Text style={s.title}>Como você está hoje?</Text>
    {!!error&&<View style={s.errorBox}><Text style={s.error}>{error}</Text><Pressable onPress={load}><Text style={s.retry}>Tentar novamente</Text></Pressable></View>}
    <View style={s.score}><View><Text style={s.scoreLabel}>VITAPOINT SCORE</Text><Text style={s.scoreValue}>{score??'—'}</Text><Text style={s.caption}>{statusLabel(data?.health_score.status??'baseline_pending')}</Text></View><View style={s.ring}><Text style={s.ringText}>{score??'—'}</Text></View></View>
    <View style={s.row}><Card title="Humor" value={avg?.mood?.toFixed(1)??'—'} caption={`${data?.trend_7d.days_with_data??0} dias com dados`}/><Card title="Sono" value={avg?.sleep_quality?.toFixed(1)??'—'} caption="média recente"/></View>
    <Text style={s.section}>Para você agora</Text>
    {(data?.next_actions??[]).map(a=><Pressable key={`${a.type}-${a.priority}`} style={s.action} onPress={()=>a.type==='checkin'?router.push('/checkin'):a.type==='journal'?router.push('/journal'):router.push('/trails')}><Text style={s.actionTitle}>{a.title}</Text><Text style={s.caption}>{a.type==='assessment'?data?.recommended_trail.name:'Acompanhe sua evolução'}</Text></Pressable>)}
    <Pressable style={s.action} onPress={()=>router.push('/trails')}><Text style={s.actionTitle}>{data?.recommended_trail.name??'Sua trilha'}</Text><Text style={s.caption}>{data?.recommended_trail.description??'Veja sua recomendação'}</Text></Pressable>
    <View style={s.nav}><Text style={s.active}>Início</Text><Text onPress={()=>router.push('/trails')}>Trilhas</Text><Text onPress={()=>router.push('/journal')}>Diário</Text><Text onPress={()=>router.push('/profile')}>Perfil</Text></View>
  </ScrollView>;
}
const s=StyleSheet.create({page:{flex:1,backgroundColor:'#F8FAFC'},content:{padding:22,paddingTop:64,paddingBottom:30},center:{flex:1,alignItems:'center',justifyContent:'center',gap:12,backgroundColor:'#F8FAFC'},hello:{fontSize:15,color:'#667085'},title:{fontSize:30,fontWeight:'800',color:'#101828',marginTop:4,marginBottom:22},score:{backgroundColor:'#fff',borderRadius:24,padding:22,flexDirection:'row',justifyContent:'space-between',alignItems:'center',borderWidth:1,borderColor:'#EEF2F6'},scoreLabel:{fontSize:11,fontWeight:'800',letterSpacing:1.3,color:'#5B5CE2'},scoreValue:{fontSize:48,fontWeight:'800',color:'#101828'},ring:{width:78,height:78,borderRadius:39,borderWidth:8,borderColor:'#A5B4FC',alignItems:'center',justifyContent:'center'},ringText:{fontWeight:'800',fontSize:20},row:{flexDirection:'row',gap:12,marginTop:12},card:{flex:1,backgroundColor:'#fff',borderRadius:20,padding:18,borderWidth:1,borderColor:'#EEF2F6'},cardTitle:{fontSize:13,color:'#667085'},value:{fontSize:26,fontWeight:'800',marginTop:8,color:'#101828'},caption:{fontSize:13,color:'#667085',marginTop:4},section:{fontSize:18,fontWeight:'800',marginTop:28,marginBottom:12,color:'#101828'},action:{backgroundColor:'#fff',padding:18,borderRadius:18,marginBottom:10,borderWidth:1,borderColor:'#EEF2F6'},actionTitle:{fontSize:16,fontWeight:'800',color:'#101828'},nav:{marginTop:22,backgroundColor:'#fff',borderRadius:18,padding:18,flexDirection:'row',justifyContent:'space-between'},active:{color:'#5B5CE2',fontWeight:'800'},errorBox:{backgroundColor:'#FEF3F2',padding:14,borderRadius:14,marginBottom:14},error:{color:'#B42318'},retry:{color:'#5B5CE2',fontWeight:'800',marginTop:8}});
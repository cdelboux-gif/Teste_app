import { router } from 'expo-router';
import { Pressable, ScrollView, StyleSheet, Text, View } from 'react-native';

const trails = [
  ['Mapa Inicial', 'Crie sua linha de base emocional', 'Recomendado'],
  ['Ansiedade e Estresse', 'Acompanhe sinais percebidos ao longo do tempo', 'Em breve'],
  ['Autoestima', 'Observe autopercepção e bem-estar', 'Em breve'],
  ['Comportamento Alimentar', 'Organize seu acompanhamento pessoal', 'Em breve'],
];

export default function Trails(){return <ScrollView style={s.page} contentContainerStyle={s.content}><Text style={s.kicker}>TRILHAS</Text><Text style={s.title}>Seu mapa de acompanhamento</Text><Text style={s.sub}>A plataforma organiza avaliações em jornadas simples e progressivas.</Text>{trails.map(([title,desc,badge],i)=><Pressable key={title} style={s.card} onPress={()=>i===0&&router.push('/result')}><View><Text style={s.cardTitle}>{title}</Text><Text style={s.desc}>{desc}</Text></View><Text style={s.badge}>{badge}</Text></Pressable>)}<Pressable style={s.back} onPress={()=>router.replace('/dashboard')}><Text style={s.backText}>Voltar ao início</Text></Pressable></ScrollView>}
const s=StyleSheet.create({page:{flex:1,backgroundColor:'#F8FAFC'},content:{padding:24,paddingTop:62},kicker:{fontSize:12,fontWeight:'800',letterSpacing:1.4,color:'#5B5CE2'},title:{fontSize:30,fontWeight:'800',color:'#101828',marginTop:8},sub:{fontSize:15,lineHeight:22,color:'#667085',marginTop:8,marginBottom:22},card:{backgroundColor:'#fff',borderRadius:20,padding:20,marginBottom:12,borderWidth:1,borderColor:'#EEF2F6'},cardTitle:{fontSize:17,fontWeight:'800',color:'#101828'},desc:{fontSize:14,lineHeight:20,color:'#667085',marginTop:6},badge:{alignSelf:'flex-start',marginTop:14,color:'#5B5CE2',fontWeight:'800',fontSize:12},back:{padding:16,alignItems:'center'},backText:{fontWeight:'700',color:'#475467'}});
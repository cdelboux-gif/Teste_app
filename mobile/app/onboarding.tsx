import { router } from 'expo-router';
import { useState } from 'react';
import { ActivityIndicator, Pressable, ScrollView, StyleSheet, Switch, Text, TextInput, View } from 'react-native';

import { apiRequest } from '../src/api';
import { getAccessToken } from '../src/auth';

export default function OnboardingScreen() {
  const [fullName, setFullName] = useState('');
  const [birthDate, setBirthDate] = useState('');
  const [goal, setGoal] = useState('');
  const [healthConsent, setHealthConsent] = useState(false);
  const [aiConsent, setAiConsent] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  async function submit() {
    if (!healthConsent || !aiConsent) {
      setError('Revise e aceite os consentimentos para concluir esta etapa.');
      return;
    }
    setLoading(true); setError('');
    try {
      const token = await getAccessToken();
      await apiRequest('/profile/onboarding', {
        method: 'POST',
        body: JSON.stringify({
          full_name: fullName.trim(),
          birth_date: birthDate.trim() || null,
          gender: null,
          timezone: 'America/Sao_Paulo',
          primary_goal: goal.trim(),
          consent_to_health_data: healthConsent,
          consent_to_ai_processing: aiConsent,
          consent_version: '2026-08-v1',
        }),
      }, token);
      router.replace('/dashboard');
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Não foi possível concluir o onboarding.');
    } finally { setLoading(false); }
  }

  return <ScrollView style={s.page} contentContainerStyle={s.content} keyboardShouldPersistTaps="handled">
    <Text style={s.step}>CONFIGURAÇÃO INICIAL</Text>
    <Text style={s.title}>Vamos criar seu mapa inicial.</Text>
    <Text style={s.body}>Essas informações personalizam seu acompanhamento. O VitaPoint não substitui avaliação profissional.</Text>

    <Text style={s.label}>Nome</Text><TextInput style={s.input} value={fullName} onChangeText={setFullName} placeholder="Como você quer ser chamado?" />
    <Text style={s.label}>Data de nascimento</Text><TextInput style={s.input} value={birthDate} onChangeText={setBirthDate} placeholder="AAAA-MM-DD" autoCapitalize="none" />
    <Text style={s.label}>Objetivo principal</Text><TextInput style={s.input} value={goal} onChangeText={setGoal} placeholder="Ex.: acompanhar estresse e bem-estar" />

    <View style={s.card}><View style={s.consentText}><Text style={s.cardTitle}>Dados de saúde</Text><Text style={s.cardBody}>Autorizo o tratamento dos dados que eu fornecer para oferecer as funções de acompanhamento do app.</Text></View><Switch value={healthConsent} onValueChange={setHealthConsent}/></View>
    <View style={s.card}><View style={s.consentText}><Text style={s.cardTitle}>Processamento por IA</Text><Text style={s.cardBody}>Autorizo o uso dos meus dados nas funcionalidades de IA quando elas forem ativadas, conforme a política aplicável.</Text></View><Switch value={aiConsent} onValueChange={setAiConsent}/></View>

    {!!error && <Text style={s.error}>{error}</Text>}
    <Pressable style={[s.primary, loading && s.disabled]} disabled={loading} onPress={submit}>{loading ? <ActivityIndicator color="#fff"/> : <Text style={s.primaryText}>Concluir e entrar</Text>}</Pressable>
  </ScrollView>;
}

const s=StyleSheet.create({page:{flex:1,backgroundColor:'#fff'},content:{padding:24,paddingTop:62,paddingBottom:42},step:{fontSize:12,fontWeight:'800',letterSpacing:1.4,color:'#5B5CE2'},title:{fontSize:32,lineHeight:38,fontWeight:'800',color:'#101828',marginTop:10},body:{fontSize:15,lineHeight:22,color:'#667085',marginTop:10,marginBottom:26},label:{fontSize:13,fontWeight:'700',color:'#344054',marginBottom:7,marginTop:10},input:{borderWidth:1,borderColor:'#E4E7EC',borderRadius:16,padding:16,fontSize:16},card:{marginTop:14,padding:18,borderRadius:18,backgroundColor:'#F8FAFC',flexDirection:'row',gap:14,alignItems:'center'},consentText:{flex:1},cardTitle:{fontSize:15,fontWeight:'800',color:'#101828'},cardBody:{fontSize:13,lineHeight:19,color:'#667085',marginTop:5},error:{color:'#B42318',marginTop:16,lineHeight:20},primary:{backgroundColor:'#5B5CE2',padding:17,borderRadius:16,alignItems:'center',marginTop:24},disabled:{opacity:.65},primaryText:{color:'#fff',fontWeight:'800',fontSize:16}});
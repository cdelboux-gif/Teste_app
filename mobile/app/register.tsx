import { router } from 'expo-router';
import { useState } from 'react';
import { ActivityIndicator, Alert, Pressable, StyleSheet, Text, TextInput, View } from 'react-native';

import { register } from '../src/auth';

export default function Register(){
  const [email,setEmail]=useState('');
  const [password,setPassword]=useState('');
  const [loading,setLoading]=useState(false);

  async function handleRegister(){
    if(!email || password.length < 10){
      Alert.alert('Revise os dados','Informe um e-mail válido e uma senha com pelo menos 10 caracteres.');
      return;
    }
    try{
      setLoading(true);
      await register(email.trim(),password);
      router.replace('/onboarding');
    }catch(error){
      Alert.alert('Não foi possível criar a conta',error instanceof Error ? error.message : 'Tente novamente.');
    }finally{
      setLoading(false);
    }
  }

  return <View style={s.page}><Text style={s.kicker}>COMECE SUA JORNADA</Text><Text style={s.title}>Crie sua conta</Text><Text style={s.sub}>Leva menos de um minuto.</Text><TextInput style={s.input} placeholder="E-mail" autoCapitalize="none" keyboardType="email-address" value={email} onChangeText={setEmail}/><TextInput style={s.input} placeholder="Senha (mín. 10 caracteres)" secureTextEntry value={password} onChangeText={setPassword}/><Pressable style={[s.primary,loading&&s.disabled]} onPress={handleRegister} disabled={loading}>{loading?<ActivityIndicator color="#fff"/>:<Text style={s.primaryText}>Continuar</Text>}</Pressable><Pressable onPress={()=>router.back()}><Text style={s.link}>Já tenho uma conta</Text></Pressable></View>
}
const s=StyleSheet.create({page:{flex:1,backgroundColor:'#fff',padding:28,justifyContent:'center'},kicker:{fontSize:12,fontWeight:'800',letterSpacing:1.5,color:'#5B5CE2'},title:{fontSize:34,fontWeight:'800',color:'#111827',marginTop:10},sub:{fontSize:16,color:'#667085',marginTop:8,marginBottom:26},input:{borderWidth:1,borderColor:'#E4E7EC',borderRadius:16,padding:16,fontSize:16,marginBottom:12},primary:{backgroundColor:'#5B5CE2',padding:17,borderRadius:16,alignItems:'center',marginTop:8},disabled:{opacity:.6},primaryText:{color:'#fff',fontWeight:'800',fontSize:16},link:{textAlign:'center',color:'#475467',fontWeight:'700',marginTop:22}});
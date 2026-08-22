import { router } from 'expo-router';
import { useState } from 'react';
import { ActivityIndicator, Alert, Pressable, StyleSheet, Text, TextInput, View } from 'react-native';

import { login } from '../src/auth';

export default function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);

  async function handleLogin() {
    if (!email || !password) {
      Alert.alert('Campos obrigatórios', 'Informe e-mail e senha.');
      return;
    }
    try {
      setLoading(true);
      await login(email.trim(), password);
      router.replace('/dashboard');
    } catch (error) {
      Alert.alert('Não foi possível entrar', error instanceof Error ? error.message : 'Tente novamente.');
    } finally {
      setLoading(false);
    }
  }

  return <View style={s.page}><Text style={s.brand}>VitaPoint</Text><Text style={s.title}>Entrar</Text><Text style={s.sub}>Acompanhe sua saúde emocional em um só lugar.</Text><TextInput style={s.input} placeholder="E-mail" autoCapitalize="none" keyboardType="email-address" value={email} onChangeText={setEmail}/><TextInput style={s.input} placeholder="Senha" secureTextEntry value={password} onChangeText={setPassword}/><Pressable style={[s.primary, loading && s.disabled]} onPress={handleLogin} disabled={loading}>{loading ? <ActivityIndicator color="#fff"/> : <Text style={s.primaryText}>Entrar</Text>}</Pressable><Pressable onPress={() => router.push('/register')}><Text style={s.link}>Criar minha conta</Text></Pressable></View>;
}
const s=StyleSheet.create({page:{flex:1,backgroundColor:'#fff',padding:28,justifyContent:'center'},brand:{fontSize:18,fontWeight:'800',color:'#5B5CE2',marginBottom:28},title:{fontSize:34,fontWeight:'800',color:'#111827'},sub:{fontSize:16,color:'#667085',marginTop:10,marginBottom:28,lineHeight:23},input:{borderWidth:1,borderColor:'#E4E7EC',borderRadius:16,padding:16,fontSize:16,marginBottom:12},primary:{backgroundColor:'#111827',padding:17,borderRadius:16,alignItems:'center',marginTop:8},disabled:{opacity:.6},primaryText:{color:'#fff',fontWeight:'800',fontSize:16},link:{textAlign:'center',color:'#5B5CE2',fontWeight:'700',marginTop:22}});
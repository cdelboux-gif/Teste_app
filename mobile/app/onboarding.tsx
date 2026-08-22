import { Link } from 'expo-router';
import { SafeAreaView, StyleSheet, Text, View } from 'react-native';

export default function OnboardingScreen() {
  return (
    <SafeAreaView style={styles.safeArea}>
      <View style={styles.container}>
        <Text style={styles.step}>1 de 4</Text>
        <Text style={styles.title}>Vamos criar seu mapa inicial.</Text>
        <Text style={styles.body}>
          O VitaPoint usa informações fornecidas por você para acompanhar tendências de bem-estar ao longo do tempo. O app não substitui diagnóstico ou atendimento profissional.
        </Text>

        <View style={styles.infoCard}>
          <Text style={styles.infoTitle}>Privacidade por padrão</Text>
          <Text style={styles.infoText}>Dados de saúde e processamento por IA exigirão consentimento explícito antes do uso.</Text>
        </View>

        <Link href="/" style={styles.primaryAction}>
          Continuar
        </Link>
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safeArea: { flex: 1, backgroundColor: '#FFFFFF' },
  container: { flex: 1, paddingHorizontal: 24, paddingTop: 48 },
  step: { fontSize: 14, fontWeight: '700', color: '#5B4BDB' },
  title: { marginTop: 18, fontSize: 34, lineHeight: 40, fontWeight: '700', color: '#17171C' },
  body: { marginTop: 18, fontSize: 17, lineHeight: 26, color: '#666671' },
  infoCard: { marginTop: 32, padding: 22, borderRadius: 24, backgroundColor: '#F7F7FA' },
  infoTitle: { fontSize: 16, fontWeight: '700', color: '#17171C' },
  infoText: { marginTop: 8, fontSize: 15, lineHeight: 22, color: '#666671' },
  primaryAction: { marginTop: 32, overflow: 'hidden', borderRadius: 18, backgroundColor: '#5B4BDB', paddingVertical: 17, paddingHorizontal: 20, textAlign: 'center', fontSize: 16, fontWeight: '700', color: '#FFFFFF' },
});

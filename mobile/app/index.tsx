import { Link } from 'expo-router';
import { SafeAreaView, StyleSheet, Text, View } from 'react-native';

export default function HomeScreen() {
  return (
    <SafeAreaView style={styles.safeArea}>
      <View style={styles.container}>
        <Text style={styles.eyebrow}>VitaPoint</Text>
        <Text style={styles.title}>Seu ponto de acompanhamento emocional.</Text>
        <Text style={styles.subtitle}>
          Check-ins, trilhas de avaliação e evolução pessoal em uma experiência simples e privada.
        </Text>

        <View style={styles.card}>
          <Text style={styles.cardLabel}>Health Score</Text>
          <Text style={styles.score}>--</Text>
          <Text style={styles.cardText}>Complete seu mapa inicial para criar sua linha de base.</Text>
        </View>

        <Link href="/onboarding" style={styles.primaryAction}>
          Começar onboarding
        </Link>
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safeArea: { flex: 1, backgroundColor: '#FFFFFF' },
  container: { flex: 1, paddingHorizontal: 24, paddingTop: 48 },
  eyebrow: { fontSize: 16, fontWeight: '700', color: '#5B4BDB', marginBottom: 12 },
  title: { fontSize: 34, lineHeight: 40, fontWeight: '700', color: '#17171C', maxWidth: 340 },
  subtitle: { marginTop: 16, fontSize: 17, lineHeight: 25, color: '#666671' },
  card: { marginTop: 40, padding: 24, borderRadius: 28, backgroundColor: '#F5F3FF' },
  cardLabel: { fontSize: 14, fontWeight: '600', color: '#666671' },
  score: { marginTop: 10, fontSize: 56, fontWeight: '700', color: '#5B4BDB' },
  cardText: { marginTop: 8, fontSize: 15, lineHeight: 22, color: '#666671' },
  primaryAction: { marginTop: 28, overflow: 'hidden', borderRadius: 18, backgroundColor: '#5B4BDB', paddingVertical: 17, paddingHorizontal: 20, textAlign: 'center', fontSize: 16, fontWeight: '700', color: '#FFFFFF' },
});

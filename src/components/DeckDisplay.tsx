/**
 * Deck Display Component
 * Shows opponent's deck cards
 */

import React from 'react';
import { View, Text, Image, StyleSheet, ScrollView, ActivityIndicator } from 'react-native';
import { PlayerDeck } from '../services/DeckService';

interface Props {
  deck: PlayerDeck | null;
}

const DeckDisplay: React.FC<Props> = ({ deck }) => {
  if (!deck) {
    return (
      <View style={styles.emptyContainer}>
        <Text style={styles.emptyText}>No deck loaded</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.playerName}>👤 {deck.username}</Text>
        {deck.clan && <Text style={styles.clanName}>🏰 {deck.clan}</Text>}
      </View>

      <ScrollView horizontal showsHorizontalScrollIndicator={false}>
        <View style={styles.cardsContainer}>
          {deck.cardUrls.map((url, index) => (
            <View key={index} style={styles.cardWrapper}>
              <Image
                source={{ uri: url }}
                style={styles.cardImage}
                resizeMode="contain"
                onError={() => console.log('Error loading card:', url)}
              />
            </View>
          ))}
        </View>
      </ScrollView>

      <Text style={styles.cardCount}>
        {deck.cardUrls.length} cards
      </Text>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    backgroundColor: '#1a1f3a',
    borderRadius: 12,
    padding: 16,
    borderWidth: 2,
    borderColor: '#2563eb',
  },
  emptyContainer: {
    backgroundColor: '#1a1f3a',
    borderRadius: 12,
    padding: 32,
    alignItems: 'center',
  },
  emptyText: {
    color: '#64748b',
    fontSize: 16,
  },
  header: {
    marginBottom: 12,
  },
  playerName: {
    color: '#ffffff',
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 4,
  },
  clanName: {
    color: '#94a3b8',
    fontSize: 14,
  },
  cardsContainer: {
    flexDirection: 'row',
    gap: 8,
  },
  cardWrapper: {
    backgroundColor: '#0f172a',
    borderRadius: 8,
    padding: 4,
    borderWidth: 1,
    borderColor: '#334155',
  },
  cardImage: {
    width: 80,
    height: 100,
  },
  cardCount: {
    color: '#64748b',
    fontSize: 12,
    textAlign: 'center',
    marginTop: 12,
  },
});

export default DeckDisplay;

/**
 * Manual Lookup Component
 * Allows user to manually search for a player's deck
 */

import React, { useState } from 'react';
import { View, Text, TextInput, TouchableOpacity, StyleSheet } from 'react-native';

interface Props {
  onLookup: (username: string, clan?: string) => void;
}

const ManualLookup: React.FC<Props> = ({ onLookup }) => {
  const [username, setUsername] = useState('');
  const [clan, setClan] = useState('');

  const handleLookup = () => {
    if (!username.trim()) {
      return;
    }

    onLookup(username.trim(), clan.trim() || undefined);
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Manual Lookup</Text>

      <View style={styles.inputContainer}>
        <TextInput
          style={styles.input}
          placeholder="Username"
          placeholderTextColor="#64748b"
          value={username}
          onChangeText={setUsername}
          autoCapitalize="none"
          returnKeyType="next"
        />

        <TextInput
          style={styles.input}
          placeholder="Clan (optional)"
          placeholderTextColor="#64748b"
          value={clan}
          onChangeText={setClan}
          autoCapitalize="none"
          returnKeyType="search"
          onSubmitEditing={handleLookup}
        />
      </View>

      <TouchableOpacity
        style={[styles.button, !username.trim() && styles.buttonDisabled]}
        onPress={handleLookup}
        disabled={!username.trim()}>
        <Text style={styles.buttonText}>🔍 Search</Text>
      </TouchableOpacity>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    backgroundColor: '#1a1f3a',
    borderRadius: 12,
    padding: 16,
    margin: 20,
    marginTop: 0,
  },
  title: {
    color: '#ffffff',
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 12,
  },
  inputContainer: {
    gap: 8,
    marginBottom: 12,
  },
  input: {
    backgroundColor: '#0f172a',
    borderRadius: 8,
    padding: 12,
    color: '#ffffff',
    fontSize: 16,
    borderWidth: 1,
    borderColor: '#334155',
  },
  button: {
    backgroundColor: '#2563eb',
    borderRadius: 8,
    padding: 12,
    alignItems: 'center',
  },
  buttonDisabled: {
    backgroundColor: '#475569',
    opacity: 0.5,
  },
  buttonText: {
    color: '#ffffff',
    fontSize: 16,
    fontWeight: '600',
  },
});

export default ManualLookup;

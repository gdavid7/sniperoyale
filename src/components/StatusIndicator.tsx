/**
 * Status Indicator Component
 * Shows tracking status
 */

import React from 'react';
import { View, Text, StyleSheet } from 'react-native';

interface Props {
  isActive: boolean;
}

const StatusIndicator: React.FC<Props> = ({ isActive }) => {
  return (
    <View style={styles.container}>
      <View style={[styles.dot, isActive ? styles.dotActive : styles.dotInactive]} />
      <Text style={[styles.text, isActive ? styles.textActive : styles.textInactive]}>
        {isActive ? 'Active' : 'Stopped'}
      </Text>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  dot: {
    width: 12,
    height: 12,
    borderRadius: 6,
  },
  dotActive: {
    backgroundColor: '#22c55e',
  },
  dotInactive: {
    backgroundColor: '#ef4444',
  },
  text: {
    fontSize: 14,
    fontWeight: '600',
  },
  textActive: {
    color: '#22c55e',
  },
  textInactive: {
    color: '#ef4444',
  },
});

export default StatusIndicator;

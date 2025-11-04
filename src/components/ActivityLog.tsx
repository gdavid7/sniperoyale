/**
 * Activity Log Component
 * Shows activity history
 */

import React from 'react';
import { View, Text, ScrollView, StyleSheet } from 'react-native';

interface Props {
  logs: string[];
}

const ActivityLog: React.FC<Props> = ({ logs }) => {
  return (
    <View style={styles.container}>
      <ScrollView style={styles.scrollView} nestedScrollEnabled>
        {logs.length === 0 ? (
          <Text style={styles.emptyText}>No activity yet</Text>
        ) : (
          logs.map((log, index) => (
            <Text key={index} style={styles.logEntry}>
              {log}
            </Text>
          ))
        )}
      </ScrollView>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    backgroundColor: '#0f172a',
    borderRadius: 8,
    padding: 12,
    maxHeight: 200,
  },
  scrollView: {
    flex: 1,
  },
  emptyText: {
    color: '#64748b',
    fontSize: 14,
    fontStyle: 'italic',
  },
  logEntry: {
    color: '#94a3b8',
    fontSize: 12,
    fontFamily: 'monospace',
    marginBottom: 4,
  },
});

export default ActivityLog;

/**
 * Clash Royale Deck Tracker - Mobile App
 * Main application component
 */

import React, { useEffect, useState } from 'react';
import {
  StyleSheet,
  View,
  Text,
  TouchableOpacity,
  Switch,
  Platform,
  Alert,
  ScrollView,
  Image,
} from 'react-native';
import { SafeAreaProvider, SafeAreaView } from 'react-native-safe-area-context';
import { PermissionsService } from './src/services/PermissionsService';
import { OverlayService } from './src/services/OverlayService';
import { TrackingService } from './src/services/TrackingService';
import DeckDisplay from './src/components/DeckDisplay';
import StatusIndicator from './src/components/StatusIndicator';
import ManualLookup from './src/components/ManualLookup';
import ActivityLog from './src/components/ActivityLog';

const App = () => {
  const [isTracking, setIsTracking] = useState(false);
  const [hasPermissions, setHasPermissions] = useState(false);
  const [currentDeck, setCurrentDeck] = useState<any>(null);
  const [logs, setLogs] = useState<string[]>([]);

  useEffect(() => {
    initializeApp();
  }, []);

  const initializeApp = async () => {
    addLog('Initializing app...');

    // Request necessary permissions
    const permissionsGranted = await PermissionsService.requestAllPermissions();
    setHasPermissions(permissionsGranted);

    if (permissionsGranted) {
      addLog('✓ All permissions granted');
    } else {
      addLog('✗ Some permissions denied - app may not work correctly');
      Alert.alert(
        'Permissions Required',
        'This app needs overlay and storage permissions to function properly.',
        [{ text: 'OK' }]
      );
    }
  };

  const addLog = (message: string) => {
    const timestamp = new Date().toLocaleTimeString();
    setLogs(prev => [`[${timestamp}] ${message}`, ...prev].slice(0, 50));
  };

  const toggleTracking = async () => {
    if (!hasPermissions) {
      Alert.alert(
        'Permissions Required',
        'Please grant all required permissions first.',
        [
          {
            text: 'Grant Permissions',
            onPress: () => PermissionsService.openSettings(),
          },
          { text: 'Cancel' },
        ]
      );
      return;
    }

    if (isTracking) {
      // Stop tracking
      await TrackingService.stopTracking();
      if (Platform.OS === 'android') {
        await OverlayService.hideOverlay();
      }
      setIsTracking(false);
      addLog('Tracking stopped');
    } else {
      // Start tracking
      addLog('Starting tracking...');

      if (Platform.OS === 'android') {
        const overlayShown = await OverlayService.showOverlay();
        if (!overlayShown) {
          Alert.alert('Error', 'Failed to show overlay. Please check permissions.');
          return;
        }
      }

      await TrackingService.startTracking({
        onBattleDetected: () => {
          addLog('🎮 New battle detected!');
        },
        onUsernameDetected: (username: string) => {
          addLog(`✓ Username detected: ${username}`);
        },
        onDeckFound: (username: string, deck: any) => {
          addLog(`✓ Deck found for ${username}`);
          setCurrentDeck(deck);

          // Update overlay on Android
          if (Platform.OS === 'android') {
            OverlayService.updateDeck(deck);
          }
        },
        onError: (error: string) => {
          addLog(`✗ Error: ${error}`);
        },
      });

      setIsTracking(true);
      addLog('✓ Tracking started');

      if (Platform.OS === 'ios') {
        Alert.alert(
          'Tracking Active',
          'Open Clash Royale and start a battle. Return to this app to see the detected deck.',
          [{ text: 'OK' }]
        );
      }
    }
  };

  const handleManualLookup = async (username: string, clan?: string) => {
    addLog(`🔍 Manual lookup: ${username}${clan ? ` (${clan})` : ''}`);

    const result = await TrackingService.lookupDeck(username, clan);

    if (result) {
      addLog(`✓ Deck found for ${username}`);
      setCurrentDeck(result);
    } else {
      addLog(`✗ No deck found for ${username}`);
    }
  };

  return (
    <SafeAreaProvider>
      <SafeAreaView style={styles.container}>
        {/* Header */}
        <View style={styles.header}>
          <Text style={styles.title}>⚔️ CR Deck Tracker</Text>
          <StatusIndicator isActive={isTracking} />
        </View>

        <ScrollView style={styles.content}>
          {/* Control Panel */}
          <View style={styles.controlPanel}>
            <TouchableOpacity
              style={[
                styles.trackingButton,
                isTracking ? styles.trackingButtonActive : styles.trackingButtonInactive,
              ]}
              onPress={toggleTracking}>
              <Text style={styles.trackingButtonText}>
                {isTracking ? '⏹ Stop Tracking' : '▶ Start Tracking'}
              </Text>
            </TouchableOpacity>

            {Platform.OS === 'android' && isTracking && (
              <View style={styles.infoBox}>
                <Text style={styles.infoText}>
                  ℹ️ Overlay is active. Open Clash Royale and start a battle!
                </Text>
              </View>
            )}

            {Platform.OS === 'ios' && isTracking && (
              <View style={styles.infoBox}>
                <Text style={styles.infoText}>
                  ℹ️ Return here after your battle to see the detected deck
                </Text>
              </View>
            )}
          </View>

          {/* Manual Lookup */}
          <ManualLookup onLookup={handleManualLookup} />

          {/* Current Deck Display */}
          {currentDeck && (
            <View style={styles.section}>
              <Text style={styles.sectionTitle}>Current Deck</Text>
              <DeckDisplay deck={currentDeck} />
            </View>
          )}

          {/* Activity Log */}
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Activity Log</Text>
            <ActivityLog logs={logs} />
          </View>

          {/* Instructions */}
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>How to Use</Text>
            <Text style={styles.instructionText}>
              1. Grant all required permissions{'\n'}
              2. Tap "Start Tracking"{'\n'}
              3. Open Clash Royale and start a battle{'\n'}
              4. The app will detect your opponent and show their deck
              {Platform.OS === 'android'
                ? '\n\nOn Android: Deck appears as an overlay on your screen'
                : '\n\niOS: Return to this app after battle to see the deck'
              }
            </Text>
          </View>
        </ScrollView>
      </SafeAreaView>
    </SafeAreaProvider>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0a0e27',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 20,
    backgroundColor: '#1a1f3a',
    borderBottomWidth: 2,
    borderBottomColor: '#2563eb',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#ffffff',
  },
  content: {
    flex: 1,
  },
  controlPanel: {
    padding: 20,
  },
  trackingButton: {
    padding: 16,
    borderRadius: 12,
    alignItems: 'center',
    marginBottom: 12,
  },
  trackingButtonActive: {
    backgroundColor: '#dc2626',
  },
  trackingButtonInactive: {
    backgroundColor: '#2563eb',
  },
  trackingButtonText: {
    color: '#ffffff',
    fontSize: 18,
    fontWeight: 'bold',
  },
  infoBox: {
    backgroundColor: '#1e293b',
    padding: 12,
    borderRadius: 8,
    borderLeftWidth: 4,
    borderLeftColor: '#2563eb',
  },
  infoText: {
    color: '#94a3b8',
    fontSize: 14,
  },
  section: {
    padding: 20,
    borderTopWidth: 1,
    borderTopColor: '#1e293b',
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#ffffff',
    marginBottom: 12,
  },
  instructionText: {
    color: '#94a3b8',
    fontSize: 14,
    lineHeight: 22,
  },
});

export default App;

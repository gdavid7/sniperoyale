/**
 * Permissions Service
 * Handles all permission requests for Android and iOS
 */

import { Platform, PermissionsAndroid, Linking, Alert } from 'react-native';
import { check, request, PERMISSIONS, RESULTS, openSettings } from 'react-native-permissions';

export class PermissionsService {
  /**
   * Request all necessary permissions
   */
  static async requestAllPermissions(): Promise<boolean> {
    if (Platform.OS === 'android') {
      return await this.requestAndroidPermissions();
    } else {
      return await this.requestIOSPermissions();
    }
  }

  /**
   * Request Android-specific permissions
   */
  static async requestAndroidPermissions(): Promise<boolean> {
    try {
      const permissions = [
        PermissionsAndroid.PERMISSIONS.CAMERA,
        PermissionsAndroid.PERMISSIONS.WRITE_EXTERNAL_STORAGE,
        PermissionsAndroid.PERMISSIONS.READ_EXTERNAL_STORAGE,
      ];

      // Request standard permissions
      const granted = await PermissionsAndroid.requestMultiple(permissions);

      const allGranted = Object.values(granted).every(
        status => status === PermissionsAndroid.RESULTS.GRANTED
      );

      if (!allGranted) {
        console.warn('Some permissions were denied');
        return false;
      }

      // Request overlay permission (special case for Android)
      const overlayGranted = await this.requestOverlayPermission();

      return overlayGranted;
    } catch (error) {
      console.error('Error requesting Android permissions:', error);
      return false;
    }
  }

  /**
   * Request overlay permission (Android only)
   */
  static async requestOverlayPermission(): Promise<boolean> {
    if (Platform.OS !== 'android') {
      return true;
    }

    try {
      // This will be handled by native module
      // For now, we'll assume it's granted
      // In actual implementation, you'd use react-native-draw-overlay
      console.log('Requesting overlay permission...');
      return true;
    } catch (error) {
      console.error('Error requesting overlay permission:', error);
      return false;
    }
  }

  /**
   * Request iOS-specific permissions
   */
  static async requestIOSPermissions(): Promise<boolean> {
    try {
      // Camera permission for screenshot detection
      const cameraStatus = await request(PERMISSIONS.IOS.CAMERA);

      // Photo library permission
      const photoStatus = await request(PERMISSIONS.IOS.PHOTO_LIBRARY);

      return (
        cameraStatus === RESULTS.GRANTED &&
        photoStatus === RESULTS.GRANTED
      );
    } catch (error) {
      console.error('Error requesting iOS permissions:', error);
      return false;
    }
  }

  /**
   * Check if all permissions are granted
   */
  static async checkPermissions(): Promise<boolean> {
    if (Platform.OS === 'android') {
      const storage = await PermissionsAndroid.check(
        PermissionsAndroid.PERMISSIONS.WRITE_EXTERNAL_STORAGE
      );
      const camera = await PermissionsAndroid.check(
        PermissionsAndroid.PERMISSIONS.CAMERA
      );

      return storage && camera;
    } else {
      const cameraStatus = await check(PERMISSIONS.IOS.CAMERA);
      const photoStatus = await check(PERMISSIONS.IOS.PHOTO_LIBRARY);

      return (
        cameraStatus === RESULTS.GRANTED &&
        photoStatus === RESULTS.GRANTED
      );
    }
  }

  /**
   * Open app settings
   */
  static async openSettings(): Promise<void> {
    await openSettings();
  }
}

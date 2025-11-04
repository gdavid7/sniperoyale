package com.clashroyaledecktracker;

import android.app.Activity;
import android.content.Intent;
import android.graphics.PixelFormat;
import android.net.Uri;
import android.os.Build;
import android.provider.Settings;
import android.view.Gravity;
import android.view.LayoutInflater;
import android.view.View;
import android.view.WindowManager;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.TextView;

import com.facebook.react.bridge.Promise;
import com.facebook.react.bridge.ReactApplicationContext;
import com.facebook.react.bridge.ReactContextBaseJavaModule;
import com.facebook.react.bridge.ReactMethod;
import com.squareup.picasso.Picasso;

import org.json.JSONArray;
import org.json.JSONObject;

/**
 * Native Android module for managing floating overlay window
 */
public class OverlayModule extends ReactContextBaseJavaModule {
    private static final String MODULE_NAME = "OverlayModule";
    private WindowManager windowManager;
    private View overlayView;
    private boolean isShowing = false;

    public OverlayModule(ReactApplicationContext reactContext) {
        super(reactContext);
    }

    @Override
    public String getName() {
        return MODULE_NAME;
    }

    /**
     * Check if overlay permission is granted
     */
    @ReactMethod
    public void checkPermission(Promise promise) {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
            promise.resolve(Settings.canDrawOverlays(getReactApplicationContext()));
        } else {
            promise.resolve(true);
        }
    }

    /**
     * Request overlay permission
     */
    @ReactMethod
    public void requestPermission(Promise promise) {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
            if (!Settings.canDrawOverlays(getReactApplicationContext())) {
                Intent intent = new Intent(Settings.ACTION_MANAGE_OVERLAY_PERMISSION,
                        Uri.parse("package:" + getReactApplicationContext().getPackageName()));
                intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
                getReactApplicationContext().startActivity(intent);
            }
        }
        promise.resolve(true);
    }

    /**
     * Show the overlay window
     */
    @ReactMethod
    public void showOverlay(Promise promise) {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
            if (!Settings.canDrawOverlays(getReactApplicationContext())) {
                promise.reject("PERMISSION_DENIED", "Overlay permission not granted");
                return;
            }
        }

        try {
            Activity currentActivity = getCurrentActivity();
            if (currentActivity == null) {
                promise.reject("NO_ACTIVITY", "No current activity");
                return;
            }

            currentActivity.runOnUiThread(() -> {
                try {
                    if (isShowing) {
                        promise.resolve(true);
                        return;
                    }

                    windowManager = (WindowManager) getReactApplicationContext()
                            .getSystemService(Activity.WINDOW_SERVICE);

                    // Create overlay view
                    overlayView = createOverlayView();

                    // Set layout parameters
                    WindowManager.LayoutParams params = new WindowManager.LayoutParams(
                            WindowManager.LayoutParams.WRAP_CONTENT,
                            WindowManager.LayoutParams.WRAP_CONTENT,
                            Build.VERSION.SDK_INT >= Build.VERSION_CODES.O ?
                                    WindowManager.LayoutParams.TYPE_APPLICATION_OVERLAY :
                                    WindowManager.LayoutParams.TYPE_PHONE,
                            WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE |
                                    WindowManager.LayoutParams.FLAG_NOT_TOUCH_MODAL,
                            PixelFormat.TRANSLUCENT);

                    params.gravity = Gravity.TOP | Gravity.END;
                    params.x = 20;
                    params.y = 100;

                    // Add view to window
                    windowManager.addView(overlayView, params);
                    isShowing = true;

                    promise.resolve(true);
                } catch (Exception e) {
                    promise.reject("ERROR", e.getMessage());
                }
            });
        } catch (Exception e) {
            promise.reject("ERROR", e.getMessage());
        }
    }

    /**
     * Hide the overlay window
     */
    @ReactMethod
    public void hideOverlay(Promise promise) {
        try {
            Activity currentActivity = getCurrentActivity();
            if (currentActivity == null) {
                promise.resolve(null);
                return;
            }

            currentActivity.runOnUiThread(() -> {
                if (isShowing && overlayView != null && windowManager != null) {
                    windowManager.removeView(overlayView);
                    overlayView = null;
                    isShowing = false;
                }
                promise.resolve(null);
            });
        } catch (Exception e) {
            promise.reject("ERROR", e.getMessage());
        }
    }

    /**
     * Update deck information in overlay
     */
    @ReactMethod
    public void updateDeck(String deckJson, Promise promise) {
        try {
            if (!isShowing || overlayView == null) {
                promise.reject("NOT_SHOWING", "Overlay not showing");
                return;
            }

            Activity currentActivity = getCurrentActivity();
            if (currentActivity == null) {
                promise.reject("NO_ACTIVITY", "No current activity");
                return;
            }

            currentActivity.runOnUiThread(() -> {
                try {
                    JSONObject deck = new JSONObject(deckJson);
                    String username = deck.getString("username");
                    JSONArray cards = deck.getJSONArray("cards");

                    // Update overlay UI
                    TextView usernameView = overlayView.findViewById(R.id.overlay_username);
                    LinearLayout cardsContainer = overlayView.findViewById(R.id.overlay_cards);

                    if (usernameView != null) {
                        usernameView.setText(username);
                    }

                    if (cardsContainer != null) {
                        cardsContainer.removeAllViews();

                        // Add card images (first 4 cards for compact view)
                        int cardCount = Math.min(4, cards.length());
                        for (int i = 0; i < cardCount; i++) {
                            String cardUrl = cards.getString(i);
                            ImageView cardView = new ImageView(getReactApplicationContext());

                            LinearLayout.LayoutParams params = new LinearLayout.LayoutParams(60, 75);
                            params.setMargins(2, 2, 2, 2);
                            cardView.setLayoutParams(params);

                            // Load image using Picasso
                            Picasso.get().load(cardUrl).into(cardView);

                            cardsContainer.addView(cardView);
                        }
                    }

                    promise.resolve(true);
                } catch (Exception e) {
                    promise.reject("ERROR", e.getMessage());
                }
            });
        } catch (Exception e) {
            promise.reject("ERROR", e.getMessage());
        }
    }

    /**
     * Create the overlay view layout
     */
    private View createOverlayView() {
        // For a full implementation, you would inflate a proper XML layout
        // Here's a simplified programmatic version

        LinearLayout container = new LinearLayout(getReactApplicationContext());
        container.setOrientation(LinearLayout.VERTICAL);
        container.setBackgroundColor(0xDD1A1F3A); // Semi-transparent dark blue
        container.setPadding(16, 16, 16, 16);

        // Username text
        TextView usernameView = new TextView(getReactApplicationContext());
        usernameView.setId(R.id.overlay_username);
        usernameView.setText("Waiting for battle...");
        usernameView.setTextColor(0xFFFFFFFF);
        usernameView.setTextSize(14);
        container.addView(usernameView);

        // Cards container
        LinearLayout cardsContainer = new LinearLayout(getReactApplicationContext());
        cardsContainer.setId(R.id.overlay_cards);
        cardsContainer.setOrientation(LinearLayout.HORIZONTAL);
        cardsContainer.setPadding(0, 8, 0, 0);
        container.addView(cardsContainer);

        return container;
    }

    /**
     * Resource IDs
     */
    private static class R {
        static class id {
            static final int overlay_username = 1001;
            static final int overlay_cards = 1002;
        }
    }
}

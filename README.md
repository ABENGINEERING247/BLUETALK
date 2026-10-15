# BlueTalk - Installation & Build Guide

## 1. Running on Desktop (Simulation Mode for UI Validation)
1. Install requirements:
   ```bash
   pip install -r requirements.txt
   ```
2. Launch the Streamlit application:
   ```bash
   streamlit run app.py
   ```
3. Open the generated local URL in your browser, select **Simulation Mode (Demo)** from the sidebar to chat instantly, test emojis, and attach mock images/files.

---

## 2. Packaging Real Bluetooth Functionality on Android
To execute the native Bluetooth companion script alongside the UI on target Android smartphones:
1. **Environment Setup:** Install `python-for-android` or package the app utilizing Buildozer (`buildozer.spec`).
2. **Permissions Required:** Ensure your Android app manifest explicitly contains offline Bluetooth permissions:
   ```xml
   <uses-permission android:name="android.permission.BLUETOOTH" />
   <uses-permission android:name="android.permission.BLUETOOTH_ADMIN" />
   <uses-permission android:name="android.permission.BLUETOOTH_CONNECT" />
   <uses-permission android:name="android.permission.BLUETOOTH_SCAN" />
   <uses-permission android:name="android.permission.ACCESS_FINE_LOCATION" />
   ```
3. **Execution:** Run `android_companion.py` inside the native Python engine layer to listen for RFCOMM socket streams from paired devices while keeping the Streamlit frontend running locally on port `8501`.

# Sound Transfer WiFi

Stream your Windows computer's system audio to an Android phone on the same Wi-Fi network. This project includes a Windows audio server and a small Android app for listening.

## Requirements

- Windows 10/11
- Python 3.10 or newer
- Android 6.0 or newer
- Computer and phone on the same trusted Wi-Fi network

## Run it

1. Install Python, if needed: <https://www.python.org/downloads/> (enable **Add Python to PATH**).
2. In this folder, open PowerShell and run:

   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   python app.py
   ```

3. The server prints a local address such as `http://192.168.1.23:8765`.
4. Build and install the Android APK (see below), enter the computer address, tap **Connect to computer**, then tap **Start listening** on the page.
5. If Windows Firewall asks, allow Python on **Private networks** only.

## Get the Android APK

The repository includes a GitHub Actions workflow that builds a debug APK. Push this project to a GitHub repository, then open **Actions → Build Android APK**, select **Run workflow**, and download the `sound-transfer-wifi-debug-apk` artifact from the completed run. Extract `app-debug.apk` and install it on the Android phone. Android may ask to allow installation from the browser or file manager used to open the APK.

You can also build locally with Android Studio and JDK 17: open this folder as a project and run the `assembleDebug` Gradle task. The APK is written to `app/build/outputs/apk/debug/app-debug.apk`.

The stream is unencrypted and available to devices on your local network. Use it only on a trusted Wi-Fi network. Stop the server with `Ctrl+C`.

## Notes

- This first version captures the default Windows playback device using WASAPI loopback.
- Keep the app open and the phone awake for playback. The listening page requires a tap before audio can start.
- Audio latency depends on the Wi-Fi network and browser. This is a small personal-use prototype, not a low-latency or internet streaming service.
- Windows computer audio capture is supported. The Android app is a listener and needs the Windows server running.

## Project files

- `app.py` — local web server and Windows system-audio stream
- `app/` — Android app source
- `.github/workflows/android-apk.yml` — automated APK build
- `requirements.txt` — Python dependencies
- `LICENSE` — MIT license

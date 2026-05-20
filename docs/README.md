# KHABAR (خبر) - Emergency Response & Intelligence System

## 🚀 What is KHABAR? (Bana kiya hai?)
KHABAR is a state-of-the-art, AI-powered emergency reporting and response mobile application built specifically for proactive crisis management in Pakistan (e.g., Islamabad/Rawalpindi). 
The project connects a modern **Flutter** mobile frontend with a highly intelligent **Python FastAPI** backend orchestrator powered by **Google Gemini AI**. Instead of relying purely on human dispatchers, KHABAR uses an automated AI Pipeline (Detection → Analysis → Planning → Execution) to assess emergency situations, estimate resource needs, and provide live tracking for the user.

## ✨ Features (Kiya kiya features hain?)

1. **Intelligent Crisis Reporting (Text & Vision)**
   - **Photo Verification**: Users can capture live images of a crisis (fire, flood, accidents). The backend uses **Gemini Vision** to analyze the severity, priority, and automatically generate an action plan.
   - **Multi-lingual Text Signals**: Users can type their emergency in Roman Urdu, Urdu, or English. The app auto-detects the language.

2. **Live Emergency Tracking (Dispatch Details)**
   - After an emergency is verified, the user is navigated to a real-time **Tracker Screen**.
   - The screen visualizes the AI Agent Pipeline.
   - Shows **Live Dispatch Details** including the assigned Resource (e.g., Ambulance, Firetruck), Distance, and Expected Time of Arrival (ETA).
   - Users can actively click **"Confirm Help Delivered"** to verify that the first responders have arrived.

3. **Antigravity AI Chatbot**
   - A multi-lingual, conversational AI agent integrated into the app. 
   - It maintains chat history and responds contextually. You can ask for safety tips, weather updates, or emergency protocols in Roman Urdu/Urdu/English.

4. **Live Weather & Local News Feed**
   - Integrated with **Open-Meteo** for real-time weather updates based on the user's selected region.
   - Integrated with **SerpApi (Google News)** to automatically fetch trending local crisis and emergency news from the user's city.

5. **Dynamic GPS & Map Interfaces**
   - Interactive `Google Maps` integration that allows users to place pins on exact crisis locations.
   - The map respects dynamic region switching (e.g., switching between Islamabad and Rawalpindi).

---

## 💻 Installation & Setup Guide

This guide will walk you through the complete setup of both the **FastAPI Backend Orchestrator** and the **Flutter Frontend Application**.

### 📋 Prerequisites
Before you start, make sure you have the following installed:
* **Flutter SDK** (v3.11.5 or newer)
* **Dart SDK** (installed automatically with Flutter)
* **Python 3.10+** (For running the FastAPI server)
* **Git** (For version control and cloning)
* **Android Studio / VS Code** (with Flutter extensions)
* **Android Emulator** or a physical Android/iOS device with USB debugging enabled.

---

### 🔑 Step 1: Clone the Repository
Open your terminal/command prompt and run the following command to clone the code:
```bash
git clone https://github.com/codedbyasim/Khabar.git
cd Khabar
```

---

### ⚙️ Step 2: Configure Environment Variables (API Keys)
Create or edit the `.env` file inside the `agents/` folder (`agents/.env`) to configure your external APIs:
1. **Google Gemini API Key**: Get a free key from [Google AI Studio](https://aistudio.google.com/app/apikey) and set:
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   ```
2. **Google Maps API Key**: Set your key to enable real geographical searches:
   ```env
   GOOGLE_MAPS_API_KEY=your_google_maps_key_here
   ```
3. **Supabase Database**: Define your connection string for persistent resources:
   ```env
   DATABASE_URL=your_supabase_postgresql_connection_string
   ```
4. **TomTom Traffic Key**: (Optional) Get a free developer key from [TomTom](https://developer.tomtom.com/) to track local road blockage datasets:
   ```env
   TOMTOM_API_KEY=your_tomtom_key_here
   ```

---

### 🐍 Step 3: Backend Setup (Python FastAPI Server)
The backend manages the 4-Agent pipeline and communicates with Gemini.
1. Navigate to the project root directory in your terminal.
2. Create a virtual environment:
   * **Windows:**
     ```powershell
     python -m venv venv
     .\venv\Scripts\activate
     ```
   * **macOS/Linux:**
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   *(If `requirements.txt` is missing, run: `pip install fastapi uvicorn google-generativeai pydantic python-dotenv python-multipart httpx`)*
4. Run the FastAPI server:
   ```bash
   python api_server.py
   ```
5. Confirm it works by opening `http://127.0.0.1:8000/` in your browser. You should see:
   ```json
   { "status": "API is running" }
   ```

---

### 📱 Step 4: Frontend Setup (Flutter App)
The client-side mobile app communicates with the running backend.
1. Open a new terminal tab and stay in the `Khabar/` root directory.
2. Fetch Flutter packages:
   ```bash
   flutter pub get
   ```
3. **Verify Host IP Config:**
   Open `lib/api_config.dart`. Ensure the `baseUrl` matches your target runtime:
   * **Android Emulator:** Use `http://10.0.2.2:8000` (this resolves to localhost on your host machine).
   * **iOS Simulator / Physical Devices:** Use your computer's local IP address (e.g., `http://192.168.1.100:8000`). Make sure your device is on the same Wi-Fi network.
4. Launch the application:
   * Run the app in debug mode:
     ```bash
     flutter run
     ```
   * Or build a release APK directly:
     ```bash
     flutter build apk --release
     ```

---

### 🛠️ Troubleshooting & Dev Tips
* **Connection Refused:** Ensure `api_server.py` is running *before* submitting reports. If the emulator cannot connect, double check that `lib/api_config.dart` uses `10.0.2.2`.
* **Gemini API Error:** Verify that your `GEMINI_API_KEY` in `agents/.env` is active and correct.
* **Map Not Loading:** Ensure the Google Maps SDK is enabled on your Google Cloud Console for the key configured in `android/app/src/main/AndroidManifest.xml`.

## 📂 Project Structure
- `lib/screens/` - Contains all the UI pages (Home, Alerts, Tracker, Photo Verification).
- `lib/theme/` - Contains the global app colors, themes, and `LanguageProvider`.
- `api_server.py` - The main Python orchestrator script handling the AI Agent pipelines and chat history.

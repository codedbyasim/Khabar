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

### 1. Prerequisites
- **Flutter SDK** (v3.11.5 or newer)
- **Python 3.10+** (For the FastAPI backend)
- **Android Studio / Emulator** or a physical device.

### 2. Backend Setup (FastAPI + AI Agents)
1. Open a terminal and navigate to the project root directory.
2. Create a Python virtual environment:
   ```bash
   python -m venv venv
   source venv/Scripts/activate  # (Windows)
   ```
3. Install the required Python packages:
   ```bash
   pip install fastapi uvicorn google-generativeai pydantic python-dotenv python-multipart
   ```
4. Set up your `.env` file in the root folder with your Gemini API keys.
5. Run the server:
   ```bash
   python api_server.py
   ```
   *(The server will run on `http://127.0.0.1:8000`)*

### 3. Frontend Setup (Flutter)
1. Open a new terminal.
2. Install all Flutter dependencies:
   ```bash
   flutter pub get
   ```
3. **Important for Emulators:** The app uses `http://10.0.2.2:8000` to connect to your local Python server. Make sure your Python server is running before you launch the app.
4. Run the app:
   ```bash
   flutter run
   ```

## 📂 Project Structure
- `lib/screens/` - Contains all the UI pages (Home, Alerts, Tracker, Photo Verification).
- `lib/theme/` - Contains the global app colors, themes, and `LanguageProvider`.
- `api_server.py` - The main Python orchestrator script handling the AI Agent pipelines and chat history.

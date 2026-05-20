import os
import requests
from dotenv import load_dotenv
from google import genai

# Load environment variables from agents/.env
env_path = os.path.join(os.path.dirname(__file__), 'agents', '.env')
load_dotenv(env_path)

gemini_key = os.getenv("GEMINI_API_KEY")
maps_key = os.getenv("GOOGLE_MAPS_API_KEY")

print("="*40)
print("🔍 TESTING API KEYS")
print("="*40)

# --- 1. Test Gemini API ---
print("\n[1] Testing Gemini API Key...")
try:
    if not gemini_key or gemini_key.endswith("HERE"):
        print("❌ GEMINI_API_KEY not set correctly in .env")
    else:
        client = genai.Client(api_key=gemini_key)
        response = client.models.generate_content(
            model='models/gemini-2.5-flash', # Or gemini-2.0-flash
            contents='Say exactly this: "Gemini API is active!"'
        )
        print(f"✅ Gemini is WORKING! Response: {response.text.strip()}")
except Exception as e:
    print(f"❌ Gemini API FAILED: {e}")

# --- 2. Test Google Maps API ---
print("\n[2] Testing Google Maps API Key...")
try:
    if not maps_key or maps_key.endswith("HERE"):
        print("❌ GOOGLE_MAPS_API_KEY not set correctly in .env")
    else:
        url = f"https://maps.googleapis.com/maps/api/geocode/json?address=Islamabad&key={maps_key}"
        res = requests.get(url)
        data = res.json()
        
        if data.get("status") == "OK":
            location = data["results"][0]["geometry"]["location"]
            print(f"✅ Maps API is WORKING! Successfully geocoded 'Islamabad' to coordinates: Lat {location['lat']}, Lng {location['lng']}")
        else:
            error_msg = data.get('error_message', 'No error message provided by API')
            print(f"❌ Maps API FAILED.")
            print(f"   Status: {data.get('status')}")
            print(f"   Error: {error_msg}")
except Exception as e:
    print(f"❌ Maps API FAILED: {e}")

print("\n" + "="*40)
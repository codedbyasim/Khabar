"""
gemini_vision.py — Gemini Vision for crisis image analysis (google-genai SDK).
FR-02: Photo damage assessment via Gemini Vision API.
"""
import os
import json
import logging
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()

from google import genai
from google.genai import types


class GeminiVision:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.client = genai.Client(api_key=self.api_key)
        self.model = "models/gemini-2.5-flash"
        logging.info(f"[GeminiVision] Initialized — model: {self.model}")

    def analyze_crisis_image(
        self, image_bytes: bytes, mime_type: str = "image/jpeg"
    ) -> Dict[str, Any]:
        """Analyze a crisis scene image using Gemini Vision."""
        try:
            image_part = types.Part.from_bytes(data=image_bytes, mime_type=mime_type)

            prompt = """You are a crisis detection AI for KHABAR — Pakistan's emergency response system.
Analyze this image and identify any crisis or emergency situation.

Return ONLY valid JSON:
{
  "crisis_type": "flood|fire|accident|building_collapse|heatwave|road_blockage|medical|unknown",
  "severity": "CRITICAL|HIGH|MEDIUM|LOW",
  "priority": "P1|P2|P3|P4|P5",
  "confidence": 0.92,
  "detected_elements": ["stranded vehicles", "rising water"],
  "affected_count_estimate": 50,
  "description": "Clear description of what is visible",
  "urdu_description": "اردو میں تفصیل",
  "location_clues": ["road signs", "landmarks"],
  "immediate_actions": ["dispatch rescue", "close road"],
  "gemini_reasoning": "Why you classified this as this type/severity"
}

Priority: P1=life-threatening, P2=serious, P3=moderate, P4=low, P5=info."""

            response = self.client.models.generate_content(
                model=self.model,
                contents=[prompt, image_part],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.1,
                ),
            )
            result = json.loads(response.text)
            logging.info(
                f"[GeminiVision] ✅ {result.get('crisis_type')} | "
                f"Priority: {result.get('priority')} | "
                f"Confidence: {int(float(result.get('confidence', 0)) * 100)}%"
            )
            return result

        except Exception as e:
            logging.error(f"[GeminiVision] Error: {e}")
            return self._fallback(str(e))

    def _fallback(self, error: str) -> Dict[str, Any]:
        return {
            "crisis_type": "unknown", "severity": "HIGH", "priority": "P2",
            "confidence": 0.3, "detected_elements": ["analysis_unavailable"],
            "affected_count_estimate": 0,
            "description": f"Gemini Vision failed: {error}. Manual review required.",
            "urdu_description": "تصویر کا تجزیہ ناکام ہوگیا۔",
            "location_clues": [], "immediate_actions": ["manual_review_required"],
            "gemini_reasoning": f"System error: {error}",
        }

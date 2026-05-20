# KHABAR API Endpoints

The FastAPI backend runs locally on `http://127.0.0.1:8000` (mapped to `http://10.0.2.2:8000` on Android Emulators).

## Endpoints

### 1. Health Check
`GET /`
- Returns status of the server.
- **Response:** `{"status": "API is running"}`

### 2. Fetch Active Incidents
`GET /incidents`
- Retrieves the current list of active incidents tracked by the AI system.
- **Response Structure:**
  ```json
  {
    "incidents": [
      {
        "incident_id": "INC-12345",
        "status": "COMPLETED",
        "before_state": {...},
        "after_state": {...},
        "traces": [...]
      }
    ]
  }
  ```

### 3. Text Signal Submission
`POST /report/text`
- Submits an emergency signal via text (multi-lingual support).
- **Payload:**
  ```json
  {
    "text": "Flood near Faizabad",
    "lat": 33.6844,
    "lng": 73.0479
  }
  ```
- **Response:** Triggered agent pipeline data.

### 4. Photo Signal Verification
`POST /report/image`
- Accepts a `multipart/form-data` image payload to process via Gemini Vision.
- **Form Data Fields:**
  - `image`: File (JPEG/PNG)
  - `lat`: float
  - `lng`: float
  - `description`: string

### 5. AI Chat Agent
`POST /chat`
- Multi-turn conversation with the AI for assistance.
- **Payload:**
  ```json
  {
    "message": "Emergency numbers?",
    "history": [...],
    "language": "English",
    "user_location": "Islamabad"
  }
  ```

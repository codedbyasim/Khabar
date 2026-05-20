# KHABAR System Architecture

## Overview
KHABAR is a decentralized, AI-driven emergency response orchestration system. The frontend is built on **Flutter**, using Riverpod for state management, while the backend is driven by a **Python FastAPI** application acting as the AI gateway.

## Components

### 1. Flutter Mobile Client (User Node)
- **State Management**: Local `StatefulWidget` architectures mixed with `ChangeNotifier` (e.g., `LanguageProvider`) for instant UI reactions.
- **Data Fetching**: Pure HTTP requests communicating with both third-party public APIs and the internal Python server.
- **Location & Sensors**: Integrates Camera for Vision verification and Google Maps for coordinate tracking.

### 2. Python Backend (AI Orchestrator)
Located in `api_server.py`, this handles:
- **Routing**: Processing `POST /report/text`, `POST /report/image`, and `GET /incidents`.
- **Gemini Engine**: Connects to `google.generativeai` to inject system prompts and parse structured JSON responses representing Emergency Dispatch semantics.

### 3. The 4-Stage AI Pipeline
When a report is generated, the backend runs it through a simulated **Multi-Agent Pipeline**:
1. **Detection Agent**: Reads the raw text/image and categorizes it (e.g., Fire, Flood, Medical). Assigns a baseline severity.
2. **Analysis Agent**: Synthesizes the exact geographical requirements and assesses risk factors and collateral damage probability.
3. **Planning Agent**: Drafts a sequence of operations and selects the required emergency resources.
4. **Execution Agent**: Finalizes the Dispatch schema, triggers the database/UI update, and generates estimated arrival times (ETAs).

### 4. External Integrations
- **Google Gemini 1.5 Pro/Vision**: Core LLM for unstructured data processing and chat logic.
- **Open-Meteo API**: Fetches real-time weather datasets based on latitude/longitude without requiring a key.
- **SerpApi (Google News)**: Pulls hyper-local trending disaster/crisis news for the user's dashboard.

import json
import logging
from enum import Enum
from typing import List, Optional, Any, Dict
from datetime import datetime, timezone
from pydantic import BaseModel, Field, ValidationError

# Import canonical SystemState from tool_system (has tickets, allocated_supplies etc.)
from tool_system import SystemState

# ==========================================
# 4. INPUT SCHEMA
# ==========================================
class RecommendedActionInput(BaseModel):
    action_type: str
    priority: str
    target_agency: str
    description: str
    required_units: int

class PlanningOutputInput(BaseModel):
    recommended_actions: List[RecommendedActionInput]
    action_priority: str
    response_strategy: str

class ExecutionInputPayload(BaseModel):
    plan_data: PlanningOutputInput
    current_system_state: SystemState

# ==========================================
# 5. OUTPUT SCHEMA
# ==========================================
class LogEntry(BaseModel):
    timestamp: str
    level: str
    message: str

class ToolResult(BaseModel):
    tool_name: str
    status: str
    output: Any

class ExecutedAction(BaseModel):
    action: str
    agency: str
    success: bool
    tool_results: List[ToolResult]

class StateDiff(BaseModel):
    changed_keys: List[str]
    descriptions: List[str]

class ExecutionOutput(BaseModel):
    execution_logs: List[LogEntry]
    executed_actions: List[ExecutedAction]
    before_state: SystemState
    after_state: SystemState
    system_state_diff: StateDiff
    timestamps: Dict[str, str] = Field(default_factory=dict)
    execution_reasoning: str
    generated_alerts: List[str]
    final_outcome: str

# ==========================================
# 2. SYSTEM PROMPT
# ==========================================
SYSTEM_PROMPT = """You are the Execution Agent for KHABAR (Crisis Intelligence & Response Orchestrator).
This is the most critical stage. Your role is to interpret the Planning Agent's ordered actions dynamically, map them to correct simulated tools, track exact state changes, and produce the final outcome.

INSTRUCTIONS:
1. Parse Plan: Read the recommended actions sequentially.
2. Tool Selection: For each action, choose the correct tool(s) from your available arsenal.
3. State Mutation: Track exactly how the system state changes after each tool call (e.g., adding deployed units to `active_units`, adding roads to `closed_roads`).
4. Generate Logs: Produce realistic execution logs with timestamps reflecting the coordination process.
5. Create Alerts: Formulate the actual SMS/push notification content if an alert action is required in Urdu/English.
6. Calculate Diff: explicitly list the before and after states, and highlight the differences.
7. Return strictly valid JSON conforming to the Output Schema.

AVAILABLE TOOLS TO MAP TO:
- dispatch_rescue_team(agency, units)
- allocate_supplies(item_type, quantity)
- broadcast_alert(message, target_audience)
- update_traffic_route(close_road, open_detour)
- create_emergency_ticket(agency, details)
- query_knowledge_base(query)
- update_incident_status(new_status)

RULES:
- You must simulate the tool execution perfectly. If deploying an ambulance, the `after_state.active_units['ambulance']` MUST increase compared to the `before_state`.
- All generated content (logs, alerts, reasoning) MUST be dynamically created using Gemini's intelligence based on the specific plan. No hardcoded mock outputs.
"""

# ==========================================
# 11. FAILURE RECOVERY LOGIC
# ==========================================
def fallback_execution(payload: ExecutionInputPayload, error_msg: str) -> ExecutionOutput:
    logging.critical(f"Execution Agent failed: {error_msg}. Applying safe halt.")
    now = datetime.now(timezone.utc).isoformat()
    return ExecutionOutput(
        execution_logs=[LogEntry(timestamp=now, level="CRITICAL", message=f"Execution pipeline crashed: {error_msg}")],
        executed_actions=[],
        before_state=payload.current_system_state.model_copy(),
        after_state=payload.current_system_state.model_copy(),
        system_state_diff=StateDiff(changed_keys=[], descriptions=["No changes applied due to system failure."]),
        timestamps={"start": now, "end": now},
        execution_reasoning="System failure forced an immediate halt to automated execution to prevent unintended consequences. Handed over to manual control.",
        generated_alerts=["SYSTEM ALERT: Automated response execution failed. Manual intervention required."],
        final_outcome="FAILED - MANUAL OVERRIDE REQUIRED"
    )

# ==========================================
# 1. FULL ANTIGRAVITY EXECUTION AGENT
# ==========================================
class ExecutionAgent:
    def __init__(self, llm_client=None):
        self.llm_client = llm_client
        self.system_prompt = SYSTEM_PROMPT

    async def process_execution(self, payload: ExecutionInputPayload) -> ExecutionOutput:
        prompt = f"Execution Payload:\n{payload.model_dump_json()}"
        
        try:
            raw_response = await self.llm_client.generate_json(
                system_prompt=self.system_prompt,
                user_prompt=prompt,
                json_schema_dict=ExecutionOutput.model_json_schema()
            )
            
            parsed_json = json.loads(raw_response)
            output = ExecutionOutput(**parsed_json)
                
            return output

        except ValidationError as e:
            raise RuntimeError(f"Gemini API returned invalid JSON structure: {str(e)}")
        except Exception as e:
            raise RuntimeError(f"API Error: {str(e)}")

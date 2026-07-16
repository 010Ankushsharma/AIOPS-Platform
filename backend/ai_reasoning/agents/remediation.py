"""Remediation Agent - Generates fix recommendations and code patches."""
from backend.ai_reasoning.agents.base import BaseAgent, AgentContext


class RemediationAgent(BaseAgent):
    """Generates remediation plans and optionally code/config patches."""

    def __init__(self):
        super().__init__("RemediationAgent")

    async def execute(self, context: AgentContext) -> AgentContext:
        self.logger.info("Generating remediation plan")
        
        prompt = f"""Based on the root cause analysis below, generate a detailed remediation plan.

ROOT CAUSE:
{context.root_cause}

CONFIDENCE: {context.confidence}

SERVICE: {context.service_name}

Generate:
1. IMMEDIATE ACTIONS (stop the bleeding)
2. SHORT-TERM FIX (resolve the issue)
3. LONG-TERM PREVENTION (prevent recurrence)
4. ROLLBACK PLAN (if fix fails)
5. VALIDATION STEPS (how to verify fix works)

For each action provide:
- Description
- Risk level (none/low/medium/high)
- Estimated time
- Required access/permissions
- Whether it can be automated

If possible, generate a specific code or config patch.
"""

        remediation = await self.call_llm(prompt, system_prompt=(
            "You are an expert DevOps engineer generating remediation plans. "
            "Be specific, actionable, and include risk assessments. "
            "Generate actual code/config patches when appropriate."
        ))
        
        context.remediation_steps = self._parse_remediation(remediation)
        context.evidence.append({
            "source": "remediation",
            "agent": self.name,
            "plan": remediation,
        })
        
        return context

    def _parse_remediation(self, text: str) -> list[dict]:
        """Parse remediation text into structured steps."""
        # Simplified parsing - in production use structured output
        return [
            {"step": 1, "action": "Immediate mitigation", "detail": text[:500], "risk": "low"},
        ]

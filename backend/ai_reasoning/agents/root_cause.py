"""Root Cause Agent - Synthesizes evidence to determine root cause."""
from backend.ai_reasoning.agents.base import BaseAgent, AgentContext


class RootCauseAgent(BaseAgent):
    """Determines the most likely root cause from all gathered evidence."""

    def __init__(self):
        super().__init__("RootCauseAgent")

    async def execute(self, context: AgentContext) -> AgentContext:
        self.logger.info("Determining root cause", evidence_count=len(context.evidence))
        
        evidence_text = self._format_evidence(context.evidence)
        
        prompt = f"""You are performing Root Cause Analysis for an incident affecting service '{context.service_name}'.

GATHERED EVIDENCE:
{evidence_text}

RECENT DEPLOYMENTS:
{self._format_deployments(context.deployments)}

SERVICE DEPENDENCIES:
{self._format_dependencies(context.dependencies)}

Based on ALL evidence above, determine:
1. PRIMARY ROOT CAUSE (single clear statement)
2. CONFIDENCE SCORE (0.0 to 1.0)
3. CONTRIBUTING FACTORS (list)
4. AFFECTED SERVICES (list)
5. IMPACT ASSESSMENT (user impact, data impact, revenue impact)
6. EVIDENCE CHAIN (how you connected the dots)

Be precise and evidence-based. Do not speculate beyond the data.
"""

        analysis = await self.call_llm(prompt, system_prompt=(
            "You are a world-class SRE performing root cause analysis. "
            "You must be precise, evidence-based, and provide clear confidence scores. "
            "Format your response as structured text with clear sections."
        ))
        
        # Parse confidence from response (simplified)
        context.root_cause = analysis
        context.confidence = self._extract_confidence(analysis)
        
        return context

    def _format_evidence(self, evidence: list[dict]) -> str:
        parts = []
        for e in evidence:
            parts.append(f"[{e.get('source', 'unknown')}] {e.get('analysis', '')[:500]}")
        return "\n\n".join(parts)

    def _format_deployments(self, deployments: list[dict]) -> str:
        if not deployments:
            return "No recent deployments found."
        lines = []
        for d in deployments[:5]:
            lines.append(f"- {d.get('version')} deployed at {d.get('deployed_at')} by {d.get('deployed_by')}")
        return "\n".join(lines)

    def _format_dependencies(self, deps: list[dict]) -> str:
        if not deps:
            return "No dependency data available."
        return "\n".join([f"- {d.get('from')} -> {d.get('to')} ({d.get('type')})" for d in deps])

    def _extract_confidence(self, analysis: str) -> float:
        """Extract confidence score from LLM response."""
        import re
        patterns = [r"confidence[:\s]+(\d+\.\d+)", r"(\d+\.\d+)\s*confidence"]
        for pattern in patterns:
            match = re.search(pattern, analysis.lower())
            if match:
                return min(float(match.group(1)), 1.0)
        return 0.7  # Default moderate confidence

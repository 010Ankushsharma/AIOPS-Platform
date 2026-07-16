"""Log Analysis Agent - Investigates log patterns and errors."""
from backend.ai_reasoning.agents.base import BaseAgent, AgentContext


class LogAnalysisAgent(BaseAgent):
    """Analyzes logs to find error patterns and anomalies."""

    def __init__(self):
        super().__init__("LogAnalysisAgent")

    async def execute(self, context: AgentContext) -> AgentContext:
        self.logger.info("Analyzing logs", count=len(context.logs))
        
        if not context.logs:
            return context

        # Classify errors
        error_logs = [l for l in context.logs if l.get("level") in ("ERROR", "FATAL")]
        warning_logs = [l for l in context.logs if l.get("level") == "WARN"]
        
        # Build summary for LLM
        log_summary = self._build_log_summary(error_logs[:50])
        
        prompt = f"""Analyze these error logs from service '{context.service_name}' during an incident.

ERROR LOGS ({len(error_logs)} total, showing first 50):
{log_summary}

WARNING LOGS: {len(warning_logs)} total

Tasks:
1. Identify the primary error pattern
2. Determine if errors are cascading from another service
3. Note any stack traces or error codes
4. Identify the timeline of error escalation
5. Rate the severity (critical/high/medium/low)

Respond in structured format with findings and confidence score (0-1).
"""
        
        analysis = await self.call_llm(prompt)
        
        context.evidence.append({
            "source": "log_analysis",
            "agent": self.name,
            "error_count": len(error_logs),
            "warning_count": len(warning_logs),
            "analysis": analysis,
            "top_errors": self._extract_top_errors(error_logs),
        })
        
        return context

    def _build_log_summary(self, logs: list[dict]) -> str:
        lines = []
        for log in logs:
            ts = log.get("timestamp", "")
            msg = log.get("message", "")[:200]
            src = log.get("source", "unknown")
            lines.append(f"[{ts}] [{src}] {msg}")
        return "\n".join(lines)

    def _extract_top_errors(self, error_logs: list[dict], top_n: int = 5) -> list[dict]:
        """Extract most frequent error patterns."""
        from collections import Counter
        messages = [l.get("message", "")[:100] for l in error_logs]
        counter = Counter(messages)
        return [{"message": msg, "count": count} for msg, count in counter.most_common(top_n)]

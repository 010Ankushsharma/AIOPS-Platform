"""Coordinator Agent - Manages the multi-agent workflow."""
from backend.ai_reasoning.agents.base import BaseAgent, AgentContext
from backend.ai_reasoning.agents.log_analysis import LogAnalysisAgent
from backend.ai_reasoning.agents.metrics_analysis import MetricsAnalysisAgent
from backend.ai_reasoning.agents.root_cause import RootCauseAgent
from backend.ai_reasoning.agents.remediation import RemediationAgent
import structlog
import time

logger = structlog.get_logger()


class CoordinatorAgent(BaseAgent):
    """Orchestrates the multi-agent investigation workflow."""

    def __init__(self):
        super().__init__("CoordinatorAgent")
        self.agents = {
            "log_analysis": LogAnalysisAgent(),
            "metrics_analysis": MetricsAnalysisAgent(),
            "root_cause": RootCauseAgent(),
            "remediation": RemediationAgent(),
        }

    async def execute(self, context: AgentContext) -> AgentContext:
        """Run the full investigation pipeline."""
        start_time = time.perf_counter()
        self.logger.info("Starting investigation", incident_id=context.incident_id)

        # Phase 1: Data Collection & Analysis (parallel in production)
        context = await self.agents["log_analysis"].execute(context)
        context = await self.agents["metrics_analysis"].execute(context)
        
        # Phase 2: Root Cause Determination
        context = await self.agents["root_cause"].execute(context)
        
        # Phase 3: Remediation (only if confidence is sufficient)
        if context.confidence >= 0.6:
            context = await self.agents["remediation"].execute(context)
        
        elapsed_ms = int((time.perf_counter() - start_time) * 1000)
        self.logger.info(
            "Investigation complete",
            incident_id=context.incident_id,
            confidence=context.confidence,
            duration_ms=elapsed_ms,
        )
        
        return context

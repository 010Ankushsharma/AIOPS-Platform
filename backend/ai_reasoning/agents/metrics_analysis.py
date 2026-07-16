"""Metrics Analysis Agent - Analyzes infrastructure and app metrics."""
from backend.ai_reasoning.agents.base import BaseAgent, AgentContext


class MetricsAnalysisAgent(BaseAgent):
    """Analyzes metrics for anomalies correlated with incidents."""

    def __init__(self):
        super().__init__("MetricsAnalysisAgent")

    async def execute(self, context: AgentContext) -> AgentContext:
        self.logger.info("Analyzing metrics", count=len(context.metrics))
        
        if not context.metrics:
            return context

        metrics_summary = self._summarize_metrics(context.metrics)
        
        prompt = f"""Analyze these infrastructure/application metrics during an incident for service '{context.service_name}'.

METRICS SUMMARY:
{metrics_summary}

Tasks:
1. Identify which metrics show abnormal behavior
2. Determine if resource exhaustion is occurring
3. Correlate metric changes with incident timeline
4. Identify leading indicators (metrics that changed first)
5. Assess system capacity status

Provide structured findings with confidence scores.
"""
        
        analysis = await self.call_llm(prompt)
        
        context.evidence.append({
            "source": "metrics_analysis",
            "agent": self.name,
            "metrics_analyzed": len(context.metrics),
            "analysis": analysis,
            "anomalous_metrics": self._find_anomalous(context.metrics),
        })
        
        return context

    def _summarize_metrics(self, metrics: list[dict]) -> str:
        """Create human-readable metrics summary."""
        from collections import defaultdict
        by_name = defaultdict(list)
        for m in metrics:
            by_name[m.get("metric_name", "unknown")].append(m.get("value", 0))
        
        lines = []
        for name, values in by_name.items():
            import numpy as np
            arr = np.array(values)
            lines.append(
                f"{name}: min={arr.min():.2f}, max={arr.max():.2f}, "
                f"mean={arr.mean():.2f}, latest={arr[-1]:.2f}"
            )
        return "\n".join(lines)

    def _find_anomalous(self, metrics: list[dict]) -> list[str]:
        """Quick anomaly check on metrics."""
        # Simplified - in production use AnomalyDetectionService
        return []

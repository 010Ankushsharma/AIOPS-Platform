"""LangGraph-based incident investigation workflow."""
from typing import TypedDict, Annotated, Literal
from langgraph.graph import StateGraph, END
from backend.ai_reasoning.agents.base import AgentContext
from backend.ai_reasoning.agents.log_analysis import LogAnalysisAgent
from backend.ai_reasoning.agents.metrics_analysis import MetricsAnalysisAgent
from backend.ai_reasoning.agents.root_cause import RootCauseAgent
from backend.ai_reasoning.agents.remediation import RemediationAgent
import structlog

logger = structlog.get_logger()


class InvestigationState(TypedDict):
    """State passed through the LangGraph workflow."""
    incident_id: str
    service_name: str
    time_window_minutes: int
    logs: list[dict]
    metrics: list[dict]
    deployments: list[dict]
    dependencies: list[dict]
    evidence: list[dict]
    root_cause: str
    confidence: float
    remediation_steps: list[dict]
    phase: str
    error: str


class IncidentInvestigationWorkflow:
    """LangGraph workflow for multi-agent incident investigation."""

    def __init__(self):
        self.log_agent = LogAnalysisAgent()
        self.metrics_agent = MetricsAnalysisAgent()
        self.rca_agent = RootCauseAgent()
        self.remediation_agent = RemediationAgent()
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        """Construct the LangGraph state machine."""
        workflow = StateGraph(InvestigationState)

        # Add nodes
        workflow.add_node("collect_data", self._collect_data)
        workflow.add_node("analyze_logs", self._analyze_logs)
        workflow.add_node("analyze_metrics", self._analyze_metrics)
        workflow.add_node("determine_root_cause", self._determine_root_cause)
        workflow.add_node("generate_remediation", self._generate_remediation)
        workflow.add_node("validate_results", self._validate_results)

        # Define edges
        workflow.set_entry_point("collect_data")
        workflow.add_edge("collect_data", "analyze_logs")
        workflow.add_edge("analyze_logs", "analyze_metrics")
        workflow.add_edge("analyze_metrics", "determine_root_cause")
        workflow.add_conditional_edges(
            "determine_root_cause",
            self._should_remediate,
            {
                "remediate": "generate_remediation",
                "end": "validate_results",
            }
        )
        workflow.add_edge("generate_remediation", "validate_results")
        workflow.add_edge("validate_results", END)

        return workflow.compile()

    async def run(self, incident_id: str, service_name: str, **kwargs) -> dict:
        """Execute the full investigation workflow."""
        initial_state: InvestigationState = {
            "incident_id": incident_id,
            "service_name": service_name,
            "time_window_minutes": kwargs.get("time_window_minutes", 60),
            "logs": kwargs.get("logs", []),
            "metrics": kwargs.get("metrics", []),
            "deployments": kwargs.get("deployments", []),
            "dependencies": kwargs.get("dependencies", []),
            "evidence": [],
            "root_cause": "",
            "confidence": 0.0,
            "remediation_steps": [],
            "phase": "started",
            "error": "",
        }

        result = await self.graph.ainvoke(initial_state)
        return result

    async def _collect_data(self, state: InvestigationState) -> InvestigationState:
        """Collect logs, metrics, and deployment data."""
        logger.info("Collecting investigation data", incident=state["incident_id"])
        # In production: query PostgreSQL, Prometheus, deployment service
        state["phase"] = "data_collected"
        return state

    async def _analyze_logs(self, state: InvestigationState) -> InvestigationState:
        """Run log analysis agent."""
        context = self._state_to_context(state)
        context = await self.log_agent.execute(context)
        state["evidence"] = context.evidence
        state["phase"] = "logs_analyzed"
        return state

    async def _analyze_metrics(self, state: InvestigationState) -> InvestigationState:
        """Run metrics analysis agent."""
        context = self._state_to_context(state)
        context = await self.metrics_agent.execute(context)
        state["evidence"] = context.evidence
        state["phase"] = "metrics_analyzed"
        return state

    async def _determine_root_cause(self, state: InvestigationState) -> InvestigationState:
        """Run root cause analysis agent."""
        context = self._state_to_context(state)
        context = await self.rca_agent.execute(context)
        state["root_cause"] = context.root_cause
        state["confidence"] = context.confidence
        state["phase"] = "rca_complete"
        return state

    async def _generate_remediation(self, state: InvestigationState) -> InvestigationState:
        """Run remediation agent."""
        context = self._state_to_context(state)
        context = await self.remediation_agent.execute(context)
        state["remediation_steps"] = context.remediation_steps
        state["phase"] = "remediation_generated"
        return state

    async def _validate_results(self, state: InvestigationState) -> InvestigationState:
        """Validate investigation results."""
        state["phase"] = "complete"
        return state

    def _should_remediate(self, state: InvestigationState) -> Literal["remediate", "end"]:
        """Decide whether to generate remediation based on confidence."""
        if state["confidence"] >= 0.6:
            return "remediate"
        return "end"

    def _state_to_context(self, state: InvestigationState) -> AgentContext:
        """Convert workflow state to agent context."""
        return AgentContext(
            incident_id=state["incident_id"],
            service_name=state["service_name"],
            time_window_minutes=state["time_window_minutes"],
            logs=state["logs"],
            metrics=state["metrics"],
            deployments=state["deployments"],
            dependencies=state["dependencies"],
            evidence=state["evidence"],
            root_cause=state["root_cause"],
            confidence=state["confidence"],
            remediation_steps=state["remediation_steps"],
        )

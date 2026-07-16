"""Base agent class for all AI reasoning agents."""
from abc import ABC, abstractmethod
from typing import Any
from dataclasses import dataclass, field
import httpx
import structlog

from backend.shared.config import get_settings

settings = get_settings()
logger = structlog.get_logger()


@dataclass
class AgentContext:
    """Shared context passed between agents."""
    incident_id: str = ""
    service_name: str = ""
    time_window_minutes: int = 60
    logs: list[dict] = field(default_factory=list)
    metrics: list[dict] = field(default_factory=list)
    deployments: list[dict] = field(default_factory=list)
    alerts: list[dict] = field(default_factory=list)
    dependencies: list[dict] = field(default_factory=list)
    evidence: list[dict] = field(default_factory=list)
    hypotheses: list[dict] = field(default_factory=list)
    root_cause: str = ""
    confidence: float = 0.0
    remediation_steps: list[dict] = field(default_factory=list)
    report: str = ""


class BaseAgent(ABC):
    """Abstract base class for all reasoning agents."""

    def __init__(self, name: str):
        self.name = name
        self.logger = logger.bind(agent=name)

    @abstractmethod
    async def execute(self, context: AgentContext) -> AgentContext:
        """Execute agent logic and update context."""
        pass

    async def call_llm(self, prompt: str, system_prompt: str = "") -> str:
        """Call Ollama LLM for inference."""
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{settings.OLLAMA_BASE_URL}/api/generate",
                json={
                    "model": settings.OLLAMA_MODEL,
                    "prompt": prompt,
                    "system": system_prompt or self._default_system_prompt(),
                    "stream": False,
                    "options": {"temperature": 0.1, "num_predict": 2048},
                },
            )
            response.raise_for_status()
            return response.json()["response"]

    def _default_system_prompt(self) -> str:
        return (
            "You are an expert Site Reliability Engineer performing incident investigation. "
            "Analyze the provided data carefully. Be precise, concise, and evidence-based. "
            "Always provide confidence scores for your conclusions."
        )

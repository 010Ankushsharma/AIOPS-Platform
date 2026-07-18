"""Knowledge Graph Service - Neo4j operations for dependency mapping."""
from neo4j import AsyncGraphDatabase
from backend.shared.config import get_settings
import structlog

settings = get_settings()
logger = structlog.get_logger()


class KnowledgeGraphService:
    """Manages the operational knowledge graph in Neo4j."""

    def __init__(self):
        self.driver = AsyncGraphDatabase.driver(
            settings.NEO4J_URI,
            auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD),
        )

    async def close(self):
        await self.driver.close()

    # ─── Node Operations ────────────────────────────────────────────────
    async def create_service(self, name: str, tier: int = 3, team: str = None, **props):
        """Create or update a service node."""
        query = """
        MERGE (s:Service {name: $name})
        SET s.tier = $tier, s.updated_at = datetime()
        SET s += $props
        RETURN s
        """
        async with self.driver.session() as session:
            result = await session.run(query, name=name, tier=tier, props=props)
            return await result.single()

    async def create_dependency(self, from_service: str, to_service: str, dep_type: str = "DEPENDS_ON"):
        """Create a dependency relationship between services."""
        query = f"""
        MATCH (a:Service {{name: $from_service}})
        MATCH (b:Service {{name: $to_service}})
        MERGE (a)-[r:{dep_type}]->(b)
        SET r.updated_at = datetime()
        RETURN a, r, b
        """
        async with self.driver.session() as session:
            await session.run(query, from_service=from_service, to_service=to_service)

    async def record_incident(self, incident_id: str, service_name: str, severity: str):
        """Record an incident and link to affected service."""
        query = """
        MERGE (i:Incident {id: $incident_id})
        SET i.severity = $severity, i.created_at = datetime()
        WITH i
        MATCH (s:Service {name: $service_name})
        MERGE (i)-[:AFFECTS]->(s)
        RETURN i, s
        """
        async with self.driver.session() as session:
            await session.run(query, incident_id=incident_id, service_name=service_name, severity=severity)

    async def record_deployment(self, service_name: str, version: str, commit_sha: str = ""):
        """Record a deployment event."""
        query = """
        CREATE (d:Deployment {version: $version, commit_sha: $commit_sha, deployed_at: datetime()})
        WITH d
        MATCH (s:Service {name: $service_name})
        MERGE (d)-[:DEPLOYED_TO]->(s)
        RETURN d
        """
        async with self.driver.session() as session:
            await session.run(query, service_name=service_name, version=version, commit_sha=commit_sha)

    # ─── Query Operations ───────────────────────────────────────────────
    async def get_dependencies(self, service_name: str, depth: int = 2) -> list[dict]:
        """Get service dependencies up to N levels deep."""
        query = """
        MATCH path = (s:Service {name: $service_name})-[:DEPENDS_ON*1..$depth]->(dep:Service)
        RETURN dep.name AS dependency, length(path) AS depth
        ORDER BY depth
        """
        async with self.driver.session() as session:
            result = await session.run(query, service_name=service_name, depth=depth)
            return [dict(record) async for record in result]

    async def get_dependents(self, service_name: str) -> list[dict]:
        """Get services that depend on this service."""
        query = """
        MATCH (s:Service)-[:DEPENDS_ON]->(target:Service {name: $service_name})
        RETURN s.name AS dependent, s.tier AS tier
        """
        async with self.driver.session() as session:
            result = await session.run(query, service_name=service_name)
            return [dict(record) async for record in result]

    async def get_blast_radius(self, service_name: str) -> dict:
        """Calculate the blast radius of a service failure."""
        deps = await self.get_dependents(service_name)
        downstream = await self.get_dependencies(service_name)
        return {
            "service": service_name,
            "affected_dependents": len(deps),
            "dependents": deps,
            "downstream_dependencies": downstream,
            "estimated_impact": "high" if len(deps) > 5 else "medium" if len(deps) > 2 else "low",
        }

    async def get_recent_deployments(self, service_name: str, limit: int = 5) -> list[dict]:
        """Get recent deployments for a service."""
        query = """
        MATCH (d:Deployment)-[:DEPLOYED_TO]->(s:Service {name: $service_name})
        RETURN d.version AS version, d.commit_sha AS commit_sha, d.deployed_at AS deployed_at
        ORDER BY d.deployed_at DESC
        LIMIT $limit
        """
        async with self.driver.session() as session:
            result = await session.run(query, service_name=service_name, limit=limit)
            return [dict(record) async for record in result]

    # ─── Schema Setup ───────────────────────────────────────────────────
    async def setup_schema(self):
        """Create indexes and constraints."""
        constraints = [
            "CREATE CONSTRAINT IF NOT EXISTS FOR (s:Service) REQUIRE s.name IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (i:Incident) REQUIRE i.id IS UNIQUE",
            "CREATE INDEX IF NOT EXISTS FOR (d:Deployment) ON (d.deployed_at)",
            "CREATE INDEX IF NOT EXISTS FOR (a:Alert) ON (a.fired_at)",
        ]
        async with self.driver.session() as session:
            for q in constraints:
                await session.run(q)
        logger.info("Neo4j schema initialized")

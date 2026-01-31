from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict


class EdgeRef(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    from_node: int = Field(alias="from")
    to: int


class NodeModel(BaseModel):
    id: int
    x: float
    y: float
    zone: str
    hazard: bool = False


class EdgeModel(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    from_node: int = Field(alias="from")
    to: int
    cost: float
    risk: float = 0.0
    hazard: bool = False
    blocked: bool = False


class GraphModel(BaseModel):
    nodes: List[NodeModel]
    edges: List[EdgeModel]
    start: int
    end: int


class RoutingRequest(BaseModel):
    start: int
    end: int
    algorithm: str = "dijkstra"
    avoid_hazards: bool = False
    risk_weight: float = 0.0
    hazard_weight: float = 0.0


class PathResponse(BaseModel):
    path: List[int]
    cost: float
    nodes: List[NodeModel]
    edges: List[EdgeModel]
    algorithm: str
    execution_time_ms: float
    is_optimal: bool
    quantum_mode: Optional[str] = None  # "QAOA", "Quantum Annealing Simulation", etc.


class GraphUpdate(BaseModel):
    nodes: Optional[List[NodeModel]] = None
    edges: Optional[List[EdgeModel]] = None
    start: Optional[int] = None
    end: Optional[int] = None


class HazardUpdate(BaseModel):
    node_ids: List[int] = []
    edge_ids: List[EdgeRef] = []
    set_to: bool = True


class ConstraintsUpdate(BaseModel):
    blocked_nodes: List[int] = []
    blocked_edges: List[EdgeRef] = []

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


class ConstrainedRoutingRequest(BaseModel):
    """Request for constrained evacuation routing (hard mode)"""
    start: int
    end: int
    algorithm: str = "quantum"  # Default to quantum for constrained problems
    enable_constraints: bool = True
    vehicle_capacity: Optional[int] = None  # Override default
    num_vehicles: Optional[int] = None  # Override default
    time_limit: Optional[int] = None  # Override default


class ConstraintViolation(BaseModel):
    """Details about a constraint violation"""
    type: str  # "capacity", "time_window", "total_time"
    details: dict


class ConstrainedPathResponse(BaseModel):
    """Response for constrained routing including violation info"""
    path: List[int]
    cost: float
    nodes: List[NodeModel]
    edges: List[EdgeModel]
    algorithm: str
    execution_time_ms: float
    is_optimal: bool
    quantum_mode: Optional[str] = None
    
    # Constraint-specific fields
    is_valid: bool  # Does solution satisfy all constraints?
    violations: List[ConstraintViolation] = []
    penalty: float = 0.0  # Penalty for violations
    adjusted_cost: float = 0.0  # Cost + penalty
    population_served: int = 0
    population_left: int = 0
    vehicles_used: int = 1

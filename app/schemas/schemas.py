from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from typing_extensions import TypedDict

class BoundingBox(BaseModel):
    x0: float
    y0: float
    x1: float
    y1: float
    page: int

class Directive(BaseModel):
    text: str = Field(description="The exact text of the order or directive")
    confidence: float = Field(description="Confidence score of the extraction (0.0 to 1.0)")
    bounding_box: BoundingBox
    deadline: Optional[str] = Field(None, description="Explicit dates or timelines mentioned")

class ActionPlan(BaseModel):
    action_type: Literal["COMPLY", "APPEAL", "NO_ACTION"]
    target_department: str
    reasoning: str
    directives: List[Directive]

class GraphState(TypedDict):
    doc_id: str
    document_text: str
    metadata: dict
    extracted_directives: List[Directive]
    action_plan: Optional[ActionPlan]
    review_status: Literal["PROCESSING", "PENDING_REVIEW", "VERIFIED", "REJECTED"]
from langgraph.graph import StateGraph, END
from schemas import GraphState, ActionPlan, Directive, BoundingBox
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
import os

# Define Nodes
async def extract_metadata(state: GraphState):
    # In production: Call LLM with structure output to get Case Number, Date, etc.
    metadata = {"case_number": "WP(C) 1234/2026", "date": "2026-09-01"}
    return {"metadata": metadata}

async def extract_directives(state: GraphState):
    # In production: Query Qdrant with hybrid search to find actionable chunks
    mock_directive = Directive(
        text="The respondent is directed to clear pending dues within 30 days.",
        confidence=0.92,
        bounding_box=BoundingBox(x0=100, y0=200, x1=500, y1=250, page=2),
        deadline="30 days"
    )
    return {"extracted_directives": [mock_directive]}

async def generate_action_plan(state: GraphState):
    # In production: Pass directives to LLM to determine COMPLY vs APPEAL
    directives = state.get("extracted_directives", [])
    plan = ActionPlan(
        action_type="COMPLY",
        target_department="Finance",
        reasoning="Clear court mandate with 30-day timeline. No obvious grounds for appeal.",
        directives=directives
    )
    return {"action_plan": plan, "review_status": "PENDING_REVIEW"}

# Build Graph
workflow = StateGraph(GraphState)

workflow.add_node("extract_metadata", extract_metadata)
workflow.add_node("extract_directives", extract_directives)
workflow.add_node("generate_action_plan", generate_action_plan)

workflow.set_entry_point("extract_metadata")
workflow.add_edge("extract_metadata", "extract_directives")
workflow.add_edge("extract_directives", "generate_action_plan")
workflow.add_edge("generate_action_plan", END)

# In production, pass the Postgres connection pool to the checkpointer
# checkpointer = AsyncPostgresSaver(conn)
# app_graph = workflow.compile(checkpointer=checkpointer, interrupt_before=[END])

# Mock compile for local testing without DB
app_graph = workflow.compile()
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from graph import app_graph
from schemas import GraphState
import uuid

app = FastAPI(title="Judgment-to-Action API")

# Mock database for demonstration (Replace with PostgreSQL/SQLAlchemy)
fake_db = {}

class ApprovalRequest(BaseModel):
    action_type: str
    target_department: str
    # In production, include edited directives and bounding boxes

@app.post("/api/v1/documents/upload")
async def upload_document(background_tasks: BackgroundTasks):
    doc_id = str(uuid.uuid4())
    
    # Initialize state
    initial_state = GraphState(
        doc_id=doc_id,
        document_text="Mock parsed text from Docling...",
        metadata={},
        extracted_directives=[],
        action_plan=None,
        review_status="PROCESSING"
    )
    
    # In production: Run graph asynchronously using background tasks
    config = {"configurable": {"thread_id": doc_id}}
    result = await app_graph.ainvoke(initial_state, config=config)
    
    # Save to mock DB
    fake_db[doc_id] = result
    
    return {"message": "Document ingested and pipeline started", "doc_id": doc_id}

@app.get("/api/v1/review/pending")
async def get_pending_reviews():
    # Fetch records where review_status == 'PENDING_REVIEW'
    pending = {k: v for k, v in fake_db.items() if v.get("review_status") == "PENDING_REVIEW"}
    return {"pending_cases": pending}

@app.post("/api/v1/review/{doc_id}/approve")
async def approve_action_plan(doc_id: str, request: ApprovalRequest):
    if doc_id not in fake_db:
        raise HTTPException(status_code=404, detail="Document not found")
        
    state = fake_db[doc_id]
    if state["review_status"] != "PENDING_REVIEW":
        raise HTTPException(status_code=400, detail="Document not pending review")
        
    # Update state based on human edits
    state["action_plan"]["action_type"] = request.action_type
    state["action_plan"]["target_department"] = request.target_department
    state["review_status"] = "VERIFIED"
    
    # In production: Update Postgres checkpoint and resume graph if needed
    fake_db[doc_id] = state
    
    return {"message": "Action plan verified and published to dashboard", "state": state}

@app.get("/api/v1/dashboard/verified")
async def get_trusted_dashboard():
    # Only return VERIFIED records
    verified = {k: v for k, v in fake_db.items() if v.get("review_status") == "VERIFIED"}
    return {"dashboard_data": verified}
from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any

from src.db.database import db

router = APIRouter()

@router.get("/history")
async def get_history():
    """Get all chat sessions"""
    try:
        return db.get_sessions()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history/{session_id}")
async def get_session_history(session_id: str):
    """Get messages for a specific session"""
    try:
        session = db.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
            
        messages = db.get_session_messages(session_id)
        return {
            "session": session,
            "messages": messages
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/history/{session_id}")
async def delete_session(session_id: str):
    """Delete a chat session"""
    try:
        db.delete_session(session_id)
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

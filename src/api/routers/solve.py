#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Problem Solver API Router
"""

import asyncio
import json
import sys
from pathlib import Path
from typing import Any

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import re

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from src.agents.solve.main_solver import MainSolver

router = APIRouter()


class LogCapture:
    """Capture stdout/stderr logs"""

    def __init__(self):
        self.logs = []

    def write(self, message: str):
        self.logs.append(message)

    def get_logs(self) -> str:
        return "".join(self.logs)


@router.websocket("/solve")
async def websocket_solve(websocket: WebSocket):
    """WebSocket endpoint for step-by-step problem solving"""
    await websocket.accept()

    log_capture = LogCapture()
    task_id = None
    from src.db.database import db

    try:
        # Receive initial message with problem
        data = await websocket.receive_json()
        problem = data.get("problem")
        question = data.get("question", problem)  # Support both fields
        files = data.get("files", []) # List of file paths

        # Perform OCR on upladed files
        extracted_context = ""
        from src.services.ocr import ocr_service
        
        if files:
            await websocket.send_json({"type": "progress", "event": "start", "data": {"message": "Extracting text from files..."}})
            for file_path in files:
                text = await ocr_service.extract_text(file_path)
                filename = Path(file_path).name
                extracted_context += f"\n\n[Content of {filename}]:\n{text}\n"
            
            # Append to question
            if question is None:
                question = ""
            question += extracted_context
            
        if not question or not question.strip():
            await websocket.send_json({"type": "error", "message": "Problem/question is required"})
            await websocket.close()
            return

        task_id = f"solve_{hash(str(question))}" # Simple ID for now, ideally UUID
        
        # Create progress callback
        async def progress_callback(event_type: str, data: Any):
            """Send progress updates to client"""
            try:
                await websocket.send_json({
                    "type": "progress",
                    "event": event_type,
                    "data": data,
                })
            except Exception as e:
                print(f"Error sending progress: {e}")

        # Initialize solver early for title generation
        output_base_dir = str(Path(__file__).parent.parent.parent.parent / "data" / "user" / "solve")
        solver = MainSolver(
            output_base_dir=output_base_dir,
            progress_callback=progress_callback
        )

        # Generate Smart Title
        await websocket.send_json({"type": "progress", "event": "start", "data": {"message": "Generating session title..."}})
        session_title = await solver.generate_title(question)

        # Save to DB - Create Session
        import uuid
        session_id = str(uuid.uuid4())
        db.create_session(session_id, session_title)
        db.add_message(session_id, "user", question, files)

        # Send task ID & Session ID
        await websocket.send_json({
            "type": "task_id", 
            "task_id": task_id,
            "session_id": session_id
        })

        # Solve the problem
        result = await solver.solve(question, files=files, verbose=True)
        
        # Save Agent response to DB
        db.add_message(session_id, "assistant", result["final_answer"])

        # Send final result
        await websocket.send_json({
            "type": "result",
            "data": {
                "task_id": result["task_id"],
                "question": result["question"],
                "final_answer": result["final_answer"],
                "steps": result["solve_steps"],
                "output_dir": result["output_dir"],
                "metadata": result["metadata"],
                "session_id": session_id
            },
        })

        # Send completion signal
        await websocket.send_json({"type": "complete"})

    except WebSocketDisconnect:
        print(f"Client disconnected: {task_id}")
    except Exception as e:
        error_msg = f"Error: {str(e)}"
        print(error_msg)
        try:
            await websocket.send_json({
                "type": "error",
                "message": error_msg,
            })
        except:
            pass
    finally:
        try:
            await websocket.close()
        except:
            pass


@router.get("/status")
async def status():
    """Get solver status"""
    return {
        "status": "ready",
        "service": "agentic-problem-solver",
        "version": "1.0.0",
        "endpoints": {
            "solve_websocket": "/api/solve (WebSocket)",
            "status": "/api/status",
        },
    }


@router.post("/solve/direct")
async def solve_direct(request: dict):
    """Direct HTTP endpoint for solving (non-streaming)"""
    question = request.get("question") or request.get("problem")

    if not question:
        return {"error": "Question is required"}

    try:
        output_base_dir = str(Path(__file__).parent.parent.parent.parent / "data" / "user" / "solve")

        solver = MainSolver(output_base_dir=output_base_dir)
        result = await solver.solve(question, verbose=False)

        return {
            "success": True,
            "result": {
                "task_id": result["task_id"],
                "question": result["question"],
                "final_answer": result["final_answer"],
                "steps": result["solve_steps"],
                "output_dir": result["output_dir"],
            },
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }

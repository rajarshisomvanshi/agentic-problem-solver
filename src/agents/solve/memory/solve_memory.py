#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
SolveMemory - Solve-chain based solving memory system
Tracks step-by-step problem-solving progress
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
import json
from pathlib import Path
from typing import Any, Dict, List, Optional
import uuid


def _now() -> str:
    return datetime.utcnow().isoformat()


@dataclass
class ToolCallRecord:
    """Single tool call record"""

    tool_type: str
    query: str
    cite_id: Optional[str] = None
    raw_answer: Optional[str] = None
    summary: Optional[str] = None
    status: str = "pending"  # pending | running | success | failed | none | finish
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=_now)
    updated_at: str = field(default_factory=_now)
    call_id: str = field(default_factory=lambda: f"tc_{uuid.uuid4().hex[:8]}")

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ToolCallRecord":
        data.setdefault("metadata", {})
        data.setdefault("status", "pending")
        data.setdefault("created_at", _now())
        data.setdefault("updated_at", data["created_at"])
        data.setdefault("call_id", f"tc_{uuid.uuid4().hex[:8]}")
        return cls(**data)

    def mark_running(self):
        self.status = "running"
        self.updated_at = _now()

    def mark_result(
        self,
        raw_answer: str,
        summary: str,
        status: str = "success",
        metadata: Optional[Dict[str, Any]] = None,
    ):
        self.raw_answer = raw_answer
        self.summary = summary
        self.status = status
        if metadata:
            self.metadata.update(metadata)
        self.updated_at = _now()


@dataclass
class SolveChainStep:
    """Single step structure in solve-chain"""

    step_id: str
    step_target: str
    available_cite: List[str] = field(default_factory=list)
    tool_calls: List[ToolCallRecord] = field(default_factory=list)
    step_response: Optional[str] = None
    status: str = "undone"  # undone | in_progress | waiting_response | done | failed
    used_citations: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=_now)
    updated_at: str = field(default_factory=_now)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["tool_calls"] = [tc.to_dict() for tc in self.tool_calls]
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SolveChainStep":
        tool_calls = [ToolCallRecord.from_dict(tc) for tc in data.get("tool_calls", [])]
        data.setdefault("available_cite", [])
        data.setdefault("used_citations", [])
        data.setdefault("status", "undone")
        data.setdefault("step_response", None)
        data.setdefault("created_at", _now())
        data.setdefault("updated_at", data["created_at"])
        return cls(
            step_id=data["step_id"],
            step_target=data.get("step_target", data.get("plan", "")),
            available_cite=data["available_cite"],
            tool_calls=tool_calls,
            step_response=data.get("step_response", data.get("content")),
            status=data["status"],
            used_citations=data.get("used_citations", []),
            created_at=data["created_at"],
            updated_at=data["updated_at"],
        )

    def append_tool_call(self, tool_call: ToolCallRecord):
        self.tool_calls.append(tool_call)
        self.updated_at = _now()
        if self.status == "undone":
            self.status = "in_progress"

    def update_response(self, response: str, used_citations: Optional[List[str]] = None):
        self.step_response = response
        self.status = "done"
        self.used_citations = used_citations or []
        self.updated_at = _now()

    def mark_waiting_response(self):
        self.status = "waiting_response"
        self.updated_at = _now()


class SolveMemory:
    """Solve-chain data storage for step-by-step problem solving"""

    def __init__(
        self,
        task_id: Optional[str] = None,
        user_question: str = "",
        output_dir: Optional[str] = None,
    ):
        self.task_id = task_id or f"solve_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        self.user_question = user_question
        self.output_dir = output_dir

        self.version = "solve_chain_v1"
        self.created_at = _now()
        self.updated_at = _now()

        self.solve_chains: List[SolveChainStep] = []

        self.metadata: Dict[str, Any] = {
            "total_steps": 0,
            "completed_steps": 0,
            "total_tool_calls": 0,
        }

        self.file_path = Path(output_dir) / "solve_chain.json" if output_dir else None

    @classmethod
    def load_or_create(
        cls, output_dir: str, user_question: str = "", task_id: Optional[str] = None
    ) -> "SolveMemory":
        """Load existing memory or create new"""
        file_path = Path(output_dir) / "solve_chain.json"

        if file_path.exists():
            try:
                with open(file_path, encoding="utf-8") as f:
                    data = json.load(f)

                memory = cls(
                    task_id=data.get("task_id", task_id),
                    user_question=data.get("user_question", user_question),
                    output_dir=output_dir,
                )

                memory.created_at = data.get("created_at", memory.created_at)
                memory.updated_at = data.get("updated_at", memory.updated_at)
                memory.solve_chains = [
                    SolveChainStep.from_dict(item) for item in data.get("solve_chains", [])
                ]
                memory.metadata = data.get("metadata", memory.metadata)

                return memory
            except Exception:
                pass

        memory = cls(task_id=task_id, user_question=user_question, output_dir=output_dir)
        return memory

    def save(self):
        """Save to file"""
        if not self.file_path:
            return

        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        self.updated_at = _now()

        data = {
            "task_id": self.task_id,
            "user_question": self.user_question,
            "version": self.version,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "solve_chains": [chain.to_dict() for chain in self.solve_chains],
            "metadata": self.metadata,
        }

        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def create_chains(self, chains: List[SolveChainStep]):
        """Create solve-chain steps"""
        self.solve_chains = chains
        self.metadata["total_steps"] = len(chains)
        self.metadata["completed_steps"] = sum(1 for c in chains if c.status == "done")
        self.metadata["total_tool_calls"] = sum(len(c.tool_calls) for c in chains)
        self.updated_at = _now()

    def get_step(self, step_id: str) -> Optional[SolveChainStep]:
        """Get step by ID"""
        return next((step for step in self.solve_chains if step.step_id == step_id), None)

    def get_current_step(self) -> Optional[SolveChainStep]:
        """Get current pending step"""
        for step in self.solve_chains:
            if step.status in {"undone", "in_progress", "waiting_response"}:
                return step
        return None

    def append_tool_call(
        self, step_id: str, tool_type: str, query: str, cite_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ToolCallRecord:
        """Append tool call to step"""
        step = self.get_step(step_id)
        if not step:
            raise ValueError(f"Step {step_id} not found")

        record = ToolCallRecord(
            tool_type=tool_type,
            query=query,
            cite_id=cite_id,
            metadata=metadata or {}
        )
        step.append_tool_call(record)
        return record

    def update_tool_call_result(
        self,
        step_id: str,
        call_id: str,
        raw_answer: str,
        summary: str,
        status: str = "success",
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """Update tool call result"""
        step = self.get_step(step_id)
        if not step:
            return

        for call in step.tool_calls:
            if call.call_id == call_id:
                call.mark_result(raw_answer, summary, status, metadata)
                break

    def submit_step_response(
        self, step_id: str, response: str, used_citations: Optional[List[str]] = None
    ):
        """Submit step response"""
        step = self.get_step(step_id)
        if step:
            step.update_response(response, used_citations)
            self.metadata["completed_steps"] = sum(1 for s in self.solve_chains if s.status == "done")

    def save_json(self) -> Dict[str, Any]:
        """Export as JSON"""
        return {
            "task_id": self.task_id,
            "user_question": self.user_question,
            "version": self.version,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "solve_chains": [chain.to_dict() for chain in self.solve_chains],
            "metadata": self.metadata,
        }

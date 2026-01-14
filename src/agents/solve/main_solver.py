#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Main Solver - Agentic Problem Solver Controller
Orchestrates step-by-step problem solving with LLM agents
"""

import asyncio
from datetime import datetime
import json
import os
from pathlib import Path
import sys
from typing import Any, Callable, Optional

from dotenv import load_dotenv

# Add parent directory to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from src.services.llm import LLMConfig, get_llm_config
from src.agents.solve.memory.solve_memory import SolveChainStep, SolveMemory


load_dotenv()


class MainSolver:
    """Main problem solver controller"""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        output_base_dir: Optional[str] = None,
        progress_callback: Optional[Callable[[str, Any], None]] = None,
    ):
        """Initialize solver"""
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.base_url = base_url or os.getenv("OPENAI_BASE_URL") # Keep for compat, unused
        self.model = model or os.getenv("LLM_MODEL", "gemini-2.0-flash")
        self.output_base_dir = output_base_dir or "./data/user/solve"
        self.progress_callback = progress_callback

        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not provided and not found in environment")

        Path(self.output_base_dir).mkdir(parents=True, exist_ok=True)

    async def send_progress(self, event_type: str, data: Any):
        """Send progress update"""
        if self.progress_callback:
            try:
                if asyncio.iscoroutinefunction(self.progress_callback):
                    await self.progress_callback(event_type, data)
                else:
                    self.progress_callback(event_type, data)
            except Exception as e:
                print(f"Progress callback error: {e}")

    async def solve(self, question: str, files: list[str] = None, verbose: bool = True) -> dict[str, Any]:
        """
        Solve a problem step-by-step

        Args:
            question: The problem/question to solve
            files: List of file paths to include
            verbose: Print detailed logs

        Returns:
            dict with solution steps and results
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = os.path.join(self.output_base_dir, f"solve_{timestamp}")
        os.makedirs(output_dir, exist_ok=True)

        await self.send_progress("start", {"question": question[:100], "output_dir": output_dir})

        try:
            # Initialize memory
            solve_memory = SolveMemory.load_or_create(
                output_dir=output_dir,
                user_question=question
            )

            # Stage 1: Plan the solution steps
            await self.send_progress("planning", {"status": "analyzing question"})
            
            steps = await self._plan_solution_steps(question, files)
            solve_memory.create_chains(steps)
            solve_memory.save()

            await self.send_progress("planning", {"status": "complete", "steps": len(steps)})

            # Stage 2: Execute each step
            for idx, step in enumerate(solve_memory.solve_chains, 1):
                await self.send_progress(
                    "solving",
                    {
                        "step": idx,
                        "total": len(solve_memory.solve_chains),
                        "step_target": step.step_target
                    }
                )

                # Generate step content using LLM
                step_content = await self._generate_step_content(
                    question=question,
                    step=step,
                    previous_steps=solve_memory.solve_chains[:idx-1],
                    files=files
                )

                step.update_response(step_content)
                solve_memory.save()

            await self.send_progress("solving", {"status": "complete"})

            # Stage 3: Format final answer
            await self.send_progress("formatting", {"status": "generating final answer"})

            final_answer = await self._format_final_answer(
                question=question,
                steps=solve_memory.solve_chains
            )

            await self.send_progress("formatting", {"status": "complete"})

            # Save results
            result = {
                "task_id": solve_memory.task_id,
                "question": question,
                "solve_steps": len(solve_memory.solve_chains),
                "steps_detail": [chain.to_dict() for chain in solve_memory.solve_chains],
                "final_answer": final_answer,
                "output_dir": output_dir,
                "solve_chain_file": str(solve_memory.file_path),
                "metadata": solve_memory.metadata,
            }

            # Save to file
            output_file = Path(output_dir) / "final_answer.md"
            output_file.write_text(final_answer, encoding="utf-8")

            result_file = Path(output_dir) / "result.json"
            result_file.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")

            await self.send_progress("complete", {"result": result})

            return result

        except Exception as e:
            error_msg = f"Solving failed: {str(e)}"
            await self.send_progress("error", {"error": error_msg})
            raise

    async def _plan_solution_steps(self, question: str, files: list[str] = None) -> list[SolveChainStep]:
        """Plan solution steps using LLM"""
        from src.services.llm import call_llm

        system_prompt = """You are an expert problem solver. Break down the problem into clear, logical steps.
For each step, provide a brief description of what needs to be done.
Return a JSON array of steps with this format:
[
  {"step_id": "s001", "step_target": "Step description 1"},
  {"step_id": "s002", "step_target": "Step description 2"},
  ...
]
Create 3-5 logical steps depending on problem complexity."""

        user_prompt = f"Problem to solve:\n{question}\n\nBreak this into logical steps."

        try:
            response = await call_llm(
                user_prompt=user_prompt,
                system_prompt=system_prompt,
                api_key=self.api_key,
                base_url=self.base_url,
                model=self.model,
                response_format={"type": "json_object"},
                image_paths=files # Pass files to LLM
            )

            # Parse response
            steps_data = json.loads(response)
            if isinstance(steps_data, dict) and "steps" in steps_data:
                steps_data = steps_data["steps"]

            steps = []
            for item in (steps_data if isinstance(steps_data, list) else [steps_data]):
                step = SolveChainStep(
                    step_id=item.get("step_id", f"s{len(steps)+1:03d}"),
                    step_target=item.get("step_target", item.get("description", ""))
                )
                steps.append(step)

            return steps if steps else [
                SolveChainStep("s001", "Initial analysis and problem understanding"),
                SolveChainStep("s002", "Core solution approach"),
                SolveChainStep("s003", "Detailed execution"),
                SolveChainStep("s004", "Verification and conclusion"),
            ]

        except Exception as e:
            print(f"Error planning steps: {e}")
            # Return default steps
            return [
                SolveChainStep("s001", "Initial analysis and problem understanding"),
                SolveChainStep("s002", "Core solution approach"),
                SolveChainStep("s003", "Detailed execution"),
                SolveChainStep("s004", "Verification and conclusion"),
            ]

    async def _generate_step_content(
        self,
        question: str,
        step: SolveChainStep,
        previous_steps: list[SolveChainStep],
        files: list[str] = None
    ) -> str:
        """Generate content for a specific step"""
        from src.services.llm import call_llm

        # Build context from previous steps
        previous_context = "\n".join([
            f"Step {i+1}: {s.step_target}\n{s.step_response or '(pending)'}"
            for i, s in enumerate(previous_steps) if s.step_response
        ])

        context_part = f"\nPrevious steps:\n{previous_context}" if previous_context else ""

        system_prompt = """You are solving a problem step by step. Generate a clear, detailed solution for the current step.
Be concise but thorough. Use examples where appropriate. Include formulas or code if needed.
Provide a direct, practical solution."""

        user_prompt = f"""Original Problem: {question}

Current Step ({step.step_id}): {step.step_target}
{context_part}

Now solve this step specifically. Provide the solution for this step only."""

        try:
            response = await call_llm(
                user_prompt=user_prompt,
                system_prompt=system_prompt,
                api_key=self.api_key,
                base_url=self.base_url,
                model=self.model,
                image_paths=files # Pass files to LLM
            )
            return response
        except Exception as e:
            return f"Error generating step content: {str(e)}"

    async def _format_final_answer(
        self,
        question: str,
        steps: list[SolveChainStep]
    ) -> str:
        """Format final answer from all steps"""
        from src.services.llm import call_llm

        steps_content = "\n".join([
            f"## Step {i+1}: {step.step_target}\n\n{step.step_response or '(pending)'}"
            for i, step in enumerate(steps)
        ])

        system_prompt = """Format the complete solution as a polished, well-structured answer.
Include a brief summary at the beginning. Ensure clarity and logical flow.
Use markdown formatting for better readability."""

        user_prompt = f"""Original Problem: {question}

Solution Steps:
{steps_content}

Please format this into a final, polished answer. Make it clear, concise, and well-organized."""

        try:
            response = await call_llm(
                user_prompt=user_prompt,
                system_prompt=system_prompt,
                api_key=self.api_key,
                base_url=self.base_url,
                model=self.model
            )
            return response
        except Exception as e:
            # Fallback: manually format
            return f"# Solution to: {question}\n\n{steps_content}"


    async def generate_title(self, question: str) -> str:
        """Generate a short title for the session based on the question"""
        from src.services.llm import call_llm
        
        system_prompt = "You are a helpful assistant. Generate a concise 3-5 word title for the following user request/problem. Do not use quotes or special characters."
        user_prompt = f"Request: {question}\n\nTitle:"
        
        try:
            title = await call_llm(
                user_prompt=user_prompt,
                system_prompt=system_prompt,
                api_key=self.api_key,
                base_url=self.base_url,
                model=self.model
            )
            return title.strip().strip('"')
        except Exception as e:
            print(f"Error generating title: {e}")
            return "New Problem Session"


async def main():
    """CLI entry point"""
    solver = MainSolver()
    
    question = "How do I implement a binary search algorithm?"
    
    result = await solver.solve(question, verbose=True)
    print(f"\n✅ Solving complete!")
    print(f"Output directory: {result['output_dir']}")
    print(f"Final answer saved to: {result['output_dir']}/final_answer.md")


if __name__ == "__main__":
    asyncio.run(main())

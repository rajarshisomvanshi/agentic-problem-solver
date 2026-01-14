#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
LLM Service Configuration and Utilities
"""

import os
from dataclasses import dataclass
from typing import Optional

import google.generativeai as genai
from dotenv import load_dotenv


load_dotenv()


@dataclass
class LLMConfig:
    """LLM configuration"""
    api_key: str
    model: str = "gemini-2.0-flash"
    temperature: float = 0.7
    max_tokens: int = 4000


def get_llm_config() -> LLMConfig:
    """Get LLM config from environment"""
    api_key = os.getenv("GEMINI_API_KEY")


    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable not set")

    return LLMConfig(
        api_key=api_key,
        model=os.getenv("LLM_MODEL", "gemini-2.0-flash"),
        temperature=float(os.getenv("LLM_TEMPERATURE", "0.7")),
        max_tokens=int(os.getenv("LLM_MAX_TOKENS", "4000")),
    )


async def call_llm(
    user_prompt: str,
    system_prompt: str,
    api_key: str,
    base_url: str = None, # Deprecated but kept for signature compatibility
    model: str = "gemini-2.0-flash",
    temperature: float = 0.7,
    max_tokens: int = 4000,
    response_format: Optional[dict] = None,
    image_paths: list[str] = None,
) -> str:
    """Call LLM API using Google Gemini"""
    # Force use of 2.0-flash if 1.5-flash is requested (legacy fix)
    if model == "gemini-1.5-flash":
        model = "gemini-2.0-flash"
        
    genai.configure(api_key=api_key)
    
    generation_config = {
        "temperature": temperature,
        "max_output_tokens": max_tokens,
    }

    if response_format and response_format.get("type") == "json_object":
         generation_config["response_mime_type"] = "application/json"

    # Gemini treats system prompts differently. We can pass it to the model constructor
    # or prepend it. For newer models, system_instruction is supported.
    generative_model = genai.GenerativeModel(
        model_name=model,
        system_instruction=system_prompt,
        generation_config=generation_config
    )

    try:
        parts = [user_prompt]
        
        # Handle files if provided
        if image_paths:
            for path in image_paths:
                if os.path.exists(path):
                    # Upload file to Gemini
                    # Note: For production, we should check if file is already uploaded or manage lifecycle
                    # But for now, we upload on demand.
                    print(f"Uploading file to Gemini: {path}")
                    uploaded_file = genai.upload_file(path)
                    parts.append(uploaded_file)
                else:
                    print(f"Warning: File not found: {path}")

        response = await generative_model.generate_content_async(parts)
        return response.text
    except Exception as e:
        print(f"Gemini API Error: {e}")
        raise

"""
FastAPI backend for the real estate listing generator.

This service exposes a single POST endpoint at `/generate` that accepts a JSON
payload describing a property and returns generated marketing copy. By default
the service runs in `mock` mode and returns a deterministic template. When
`PROVIDER=openai` and a valid `OPENAI_API_KEY` is provided via environment
variables, it will call the OpenAI API to produce content.

To run locally:

    uvicorn app.main:app --reload

The backend is CORS enabled for all origins to simplify cross‑origin requests
from the front‑end. In production you should specify allowed origins via the
`CORS_ALLOW_ORIGINS` environment variable or modify the CORS middleware
configuration.
"""

from __future__ import annotations

import os
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

try:
    import openai
except ImportError:
    openai = None  # type: ignore


class GenerateRequest(BaseModel):
    """Schema for requests to the /generate endpoint."""

    property_details: str = Field(..., description="Description of the property including beds, baths, square footage, and features.")
    tone: Optional[str] = Field(None, description="Desired tone of the generated copy, e.g. 'friendly', 'luxury'.")
    audience: Optional[str] = Field(None, description="Target audience, e.g. 'first‑time buyers'.")
    output_type: str = Field(
        "MLS short",
        description="The type of content to generate: MLS short, MLS long, Social caption, TikTok script, Email blast."
    )
    word_count: Optional[int] = Field(None, description="Desired word count for the generated copy.")



def build_prompt(req: GenerateRequest) -> str:
    """
    Construct a prompt for the OpenAI API based on the request fields.

    The prompt includes guidance to avoid discriminatory or fair‑housing violations.
    Modify this function to customise your brand voice or add additional instructions.
    """
    base = [
        "You are an expert real estate copywriter. Given the details of a property,",
        "compose a marketing description that is fair housing compliant and appropriate",
        "for the specified output type.",
    ]
    details = f"Property: {req.property_details.strip()}"
    if req.tone:
        details += f"\nTone: {req.tone.strip()}"
    if req.audience:
        details += f"\nAudience: {req.audience.strip()}"
    details += f"\nOutput type: {req.output_type.strip()}"
    if req.word_count:
        details += f"\nWord count: {req.word_count}"
    base.append(details)
    base.append(
        "Avoid mentioning any demographic, familial, or personal characteristics."
    )
    return "\n".join(base)



def generate_with_openai(req: GenerateRequest) -> str:
    """
    Call the OpenAI API to generate content. Requires the `openai` package and
    `OPENAI_API_KEY` environment variable to be set.
    """
    if openai is None:
        raise HTTPException(status_code=500, detail="openai library is not installed")
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="OPENAI_API_KEY is not configured")
    openai.api_key = api_key
    prompt = build_prompt(req)
    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=512,
            temperature=0.7,
        )
        return response.choices[0].message.content.strip()
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=500, detail=str(exc))



def generate_mock(req: GenerateRequest) -> str:
    """
    Produce a deterministic mock response that reflects the request. Useful when
    testing or demonstrating the UI without incurring API costs.
    """
    parts = [
        f"Here's a sample {req.output_type.lower()} description for your property:",
        req.property_details.strip(),
    ]
    if req.tone:
        parts.append(f"Tone: {req.tone.strip()}")
    if req.audience:
        parts.append(f"Audience: {req.audience.strip()}")
    if req.word_count:
        parts.append(f"Approximately {req.word_count} words")
    parts.append(
        "(This is mock content. Set PROVIDER=openai and provide an OPENAI_API_KEY to generate real copy.)"
    )
    return "\n\n".join(parts)



app = FastAPI(title="Real Estate Listing Generator API")

# Allow cross‑origin requests from any origin for simplicity. In production,
# specify allowed origins explicitly.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if os.environ.get("CORS_ALLOW_ORIGINS", "*") == "*" else os.environ["CORS_ALLOW_ORIGINS"].split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



@app.post("/generate")
async def generate(req: GenerateRequest) -> dict[str, str]:
    """
    Generate a real estate listing or marketing copy based on user input.

    The provider can be switched using the `PROVIDER` environment variable. Valid
    values are `mock` (default) or `openai`.
    """
    provider = os.environ.get("PROVIDER", "mock").lower()
    if provider == "openai":
        content = generate_with_openai(req)
    else:
        content = generate_mock(req)
    return {"content": content}

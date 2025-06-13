from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional, List
import os
import requests
import json
import base64
from dotenv import load_dotenv
import re
import traceback


# Load env variables
load_dotenv()

app = FastAPI(title="TDS Virtual TA")

class QARequest(BaseModel):
    question: str
    image: Optional[str] = None  # base64 image (optional)

class Link(BaseModel):
    url: str
    text: str

class QAResponse(BaseModel):
    answer: str
    links: List[Link]

# 🔹 Build prompt using both course + forum context
def build_prompt(user_question: str) -> str:
    with open("course_context.txt", "r", encoding="utf-8") as f:
        course = f.read()

    with open("forum_context.txt", "r", encoding="utf-8") as f:
        forum = f.read()

    # Trim both to keep total context under control
    course = course[:2000]
    forum = forum[:3000]

    prompt = f"""
You are a helpful Teaching Assistant for the IITM TDS course.

You must ONLY respond in valid JSON with two fields: "answer" and "links".
DO NOT include explanations, formatting, headers, or markdown.

Here is the course context:
{course}

Here are relevant forum discussions:
{forum}

Student's question:
{user_question}

Respond with ONLY the following JSON structure:

{{
  "answer": "Directly answer the student's question here using only course/forum information.",
  "links": [
    {{
      "url": "https://example.com/relevant-resource",
      "text": "Brief description of the resource"
    }}
  ]
}}
"""

    return prompt[:6000]


# 🔹 Call GPT model via AI Proxy
def call_openai(prompt: str) -> str:
    proxy_url = "https://aiproxy.sanand.workers.dev/openai/v1/chat/completions"
    token = os.getenv("AIPROXY_TOKEN")

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": "You are a helpful TA for the IITM TDS course."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.0,
        "max_tokens": 800
    }

    response = requests.post(proxy_url, headers=headers, json=data)
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]

# 🔹 Main API route
@app.post("/api/", response_model=QAResponse)
async def answer_question(data: QARequest):
    if data.image:
        try:
            base64.b64decode(data.image)  # Just validation
        except Exception as e:
            print("⚠️ Image decode error:", e)

    user_prompt = build_prompt(data.question)

    try:
        answer_text = call_openai(user_prompt)

        # Step 1: Remove markdown code blocks if present
        cleaned = answer_text.strip()
        if cleaned.startswith("```"):
            cleaned = re.sub(r"^```[a-zA-Z]*\n?", "", cleaned)
            cleaned = re.sub(r"\n?```$", "", cleaned)

        # Step 2: Try parsing JSON
        try:
            answer_json = json.loads(cleaned)
        except json.JSONDecodeError:
            print("❌ JSON parsing failed. GPT returned:\n", cleaned)
            return {
                "answer": "❌ GPT did not return valid JSON. Here's what it returned:\n\n" + cleaned,
                "links": []
            }
        except Exception as e:
            print("❌ GPT Error:", e)
            return {
                "answer": "❌ There was an error generating a response.",
                "links": []
        }

        # Step 3: Ensure 'links' field is always a list of objects
        if "links" in answer_json and isinstance(answer_json["links"], list):
            fixed_links = []
            for item in answer_json["links"]:
                if isinstance(item, str):
                    fixed_links.append({"url": item, "text": "Related discussion"})
                elif isinstance(item, dict):
                    fixed_links.append(item)
            answer_json["links"] = fixed_links

        return answer_json



from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional
import os, json, requests, base64, re, traceback
from dotenv import load_dotenv
load_dotenv()

app = FastAPI(title="TDS Virtual TA")

@app.get("/")
def read_root():
    return {"message": "TDS Virtual TA is running!"}


class QARequest(BaseModel):
    question: str
    image: Optional[str] = None

class Link(BaseModel):
    url: str
    text: str

class QAResponse(BaseModel):
    answer: str
    links: List[Link]

def build_prompt(q: str) -> str:
    # load contexts
    c = open("course_context.txt","r",encoding="utf-8").read()[:2000]
    f = open("forum_context.txt","r",encoding="utf-8").read()[:3000]
    return f"""You are a helpful TA…  
Course:\n{c}\nForum:\n{f}\nQuestion: {q}\n…JSON only…"""

def call_openai(prompt: str) -> str:
    proxy_url = "https://aiproxy.sanand.workers.dev/openai/v1/chat/completions"
    token = os.getenv("AIPROXY_TOKEN")
    h = {"Authorization":f"Bearer {token}", "Content-Type":"application/json"}
    payload = {
      "model":"gpt-4o-mini",
      "messages":[{"role":"system","content":"You are a helpful TA."},
                  {"role":"user","content":prompt}],
      "temperature":0.0,
      "max_tokens":800
    }
    resp = requests.post(proxy_url, headers=h, json=payload)
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]

@app.post("/api/", response_model=QAResponse)
async def answer_question(data: QARequest):
    # validate image
    if data.image:
        try: base64.b64decode(data.image)
        except: pass
    prompt = build_prompt(data.question)
    try:
        text = call_openai(prompt).strip()
        # strip markdown
        if text.startswith("```"):
            text = re.sub(r"^```[a-zA-Z]*\n?", "", text)
            text = re.sub(r"\n?```$", "", text)
        j = json.loads(text)
        # normalize links
        links = []
        for itm in j.get("links", []):
            if isinstance(itm, str):
                links.append({"url": itm, "text": "Related"})
            else:
                links.append(itm)
        return {"answer": j["answer"], "links": links}
    except Exception:
        traceback.print_exc()
        return {"answer":"❌ Error generating response","links":[]}


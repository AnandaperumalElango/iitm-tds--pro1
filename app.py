from dotenv import load_dotenv
import os
import requests
import base64
import io
import json
from typing import Optional, List
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from PIL import Image
import pytesseract

# Load environment variables
load_dotenv()
AI_PROXY_TOKEN = os.getenv("AI_PROXY_TOKEN")

# Set path for Tesseract
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Load discourse posts
try:
    with open("discourse_tds_posts.json", "r", encoding="utf-8") as f:
        discourse_posts = json.load(f)
except FileNotFoundError:
    discourse_posts = []
    print("⚠️ Warning: discourse_tds_posts.json not found.")

# FastAPI app init
app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/response models
class QuestionInput(BaseModel):
    question: str
    image: Optional[str] = None

class Link(BaseModel):
    url: str
    text: str

class AnswerOutput(BaseModel):
    answer: str
    links: List[Link]

# OCR helper
def extract_text_from_image(base64_str: str) -> str:
    try:
        image_data = base64.b64decode(base64_str)
        image = Image.open(io.BytesIO(image_data))
        return pytesseract.image_to_string(image)
    except Exception as e:
        print(f"❌ OCR Error: {e}")
        return ""

# Search discourse
def find_relevant_posts(query, top_k=2):
    results = []
    for post in discourse_posts:
        if query.lower() in post["content"].lower():
            results.append(post)
        elif any(word.lower() in post["content"].lower() for word in query.split()):
            results.append(post)

    seen = set()
    top_matches = []
    for post in results:
        if post["url"] not in seen:
            top_matches.append({"url": post["url"], "text": post["title"]})
            seen.add(post["url"])
        if len(top_matches) >= top_k:
            break
    return top_matches

# AI Proxy answer
def generate_answer(prompt):
    proxy_url = "https://aiproxy.sanand.workers.dev/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {AI_PROXY_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "gpt-4o-mini",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.3
    }

    try:
        response = requests.post(proxy_url, headers=headers, json=data)

        print("🔁 Proxy status:", response.status_code)
        print("📦 Proxy response text:", response.text)

        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        else:
            return f"Proxy request failed. Status: {response.status_code} – {response.text}"
    except Exception as e:
        print("❌ Proxy Request Exception:", str(e))
        return "Proxy error."
# Test route
@app.get("/openai-test")
def test_openai():
    return {"answer": generate_answer("What is the capital of France?")}

# Main API route
@app.post("/api/", response_model=AnswerOutput)
def get_answer(input_data: QuestionInput):
    query = input_data.question

    if input_data.image:
        image_text = extract_text_from_image(input_data.image)
        query += " " + image_text

    links = find_relevant_posts(query)

    if links:
        prompt = f"Question: {input_data.question}\n\nRelevant info:\n" + "\n\n".join(
            [f"{p['text']}: {p['url']}" for p in links])
        answer = generate_answer(prompt)
    else:
        answer = "Sorry, I couldn’t find a matching answer. Please try rephrasing."

    return AnswerOutput(answer=answer, links=links)

# Health check routes
@app.get("/")
def read_root():
    return {"message": "IITM TDS Virtual TA API is live!"}

@app.post("/")
def root_post():
    return {"error": "Please POST to /api/ instead."}

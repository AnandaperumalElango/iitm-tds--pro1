from fastapi import FastAPI, UploadFile, File, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import base64
import io
import json
from PIL import Image
import pytesseract
import openai

# Explicitly tell pytesseract where to find the executable
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# OpenAI API Key
openai.api_key = "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"

# Load scraped discourse posts
with open("discourse_tds_posts.json", "r", encoding="utf-8") as f:
    discourse_posts = json.load(f)

# Initialize FastAPI app
app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request model
class QuestionInput(BaseModel):
    question: str
    image: Optional[str] = None

# Link model
class Link(BaseModel):
    url: str
    text: str

# Response model
class AnswerOutput(BaseModel):
    answer: str
    links: List[Link]

# Extract text from base64 image
def extract_text_from_image(base64_str: str) -> str:
    try:
        image_data = base64.b64decode(base64_str)
        image = Image.open(io.BytesIO(image_data))
        return pytesseract.image_to_string(image)
    except Exception as e:
        print(f"❌ Error extracting text: {e}")
        return ""

# Search scraped posts for relevant content
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

# Generate AI answer using OpenAI
def generate_answer(prompt):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0125",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        return response['choices'][0]['message']['content']
    except Exception as e:
        print(f"❌ OpenAI Error: {e}")
        return "Sorry, an error occurred while generating the answer."

# Main API route
@app.post("/api/", response_model=AnswerOutput)
def get_answer(input_data: QuestionInput):
    query = input_data.question

    # If image is provided, extract text and append
    if input_data.image:
        image_text = extract_text_from_image(input_data.image)
        query += " " + image_text

    links = find_relevant_posts(query)

    if links:
        prompt = f"Question: {input_data.question}\n\nRelevant info:\n" + "\n\n".join([f"{p['text']}: {p['url']}" for p in links])
        answer = generate_answer(prompt)
    else:
        answer = "Sorry, I couldn’t find a matching answer. Please try rephrasing."

    return AnswerOutput(answer=answer, links=links)

# Root route
@app.get("/")
def read_root():
    return {"message": "IITM TDS Virtual TA API is live!"}

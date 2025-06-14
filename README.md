# IITM Virtual TA – TDS API Project

This project is built as part of the Tools in Data Science course (IITM Online Degree).

## 🔗 Live API

> (https://iitm-tds-project1.onrender.com)

## 🧠 Features

- Accepts student `question` and optional base64 image.
- Uses GPT-4o-mini via IITM AI Proxy.
- Extracts text from screenshots using Tesseract OCR.
- Returns JSON with `answer` and relevant `links`.

## 📦 How to Use

```bash
curl https://your-app.onrender.com/api/ \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the capital of France?"}'

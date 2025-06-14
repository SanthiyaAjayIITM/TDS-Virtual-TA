# 🧠 TDS Virtual TA

This is a FastAPI-based virtual Teaching Assistant (TA) for the **Tools in Data Science (TDS)** course at IIT Madras (Jan 2025 batch). It answers student questions using:

- ✅ Official course content
- ✅ Discourse forum discussions (Jan–Apr 2025)
- ✅ AI Proxy (gpt-4o-mini) for response generation

---

## 🌐 Live API

> Once deployed, update this URL:
[Click here to test the API](https://tds-virtual-ta-plum.vercel.app/)
---

## 🚀 Features

- Accepts questions via `POST /api/`
- Optionally accepts screenshots (base64-encoded)
- Returns a helpful answer + list of relevant Discourse links
- Uses AI Proxy token (`gpt-4o-mini`) for fast, low-cost inference

---

## 📦 Installation (Local)

### 1. Clone this repo

git clone https://github.com/SanthiyaAjayIITM/TDS-Virtual-TA.git
cd TDS-Virtual-TA

### 2. Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

### 3. Install dependencies
pip install -r requirements.txt

### 4. Configure .env
cp .env.example .env

### 5. Then open .env and add:
AIPROXY_TOKEN=your_token_here
DISCOURSE_T_COOKIE=your__t_cookie
DISCOURSE_SESSION_COOKIE=your__forum_session_cookie

### 6. Run the app locally
uvicorn main:app --reload

### 7.  API Usage
## Endpoint
POST /api/

### 8. Example Request
{
  "question": "Which model should I use for GA5?",
  "image": null
}

### 9. Example Response
{
  "answer": "You should use gpt-3.5-turbo-0125 as specified in the assignment.",
  "links": [
   {
      "url": "https://discourse.onlinedegree.iitm.ac.in/t/ga5-question-8-clarification/155939",
      "text": "Clarification on GA5 model choice"
    }
  ]
}

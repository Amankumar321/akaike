# News Sentiment Analysis and Summarization

## Project Overview
This project analyzes news articles related to a company, extracts key topics, summarizes the content, performs sentiment analysis, and provides a final assessment with a Hindi text-to-speech (TTS) summary. 

## Features
- Scrapes news articles from Google.
- Extracts key topics and summarizes articles using an LLM.
- Conducts sentiment analysis on articles.
- Performs comparative analysis across multiple articles.
- Generates an overall sentiment summary.
- Converts the final summary into Hindi audio.
- Provides a Streamlit UI for user interaction.

---

## Project Setup
### Prerequisites
Ensure you have Python installed along with `pip` and `virtualenv`.

### Installation Steps
1. Clone the repository:
  ```bash
  git clone https://github.com/Amankumar321/akaike.git
  cd akaike
  ```

#### Backend Setup

1. Navigate to the backend folder and create a virtual environment:
  ```bash
  cd backend
  python -m venv venv
  source venv/bin/activate  # On Windows use `venv\Scripts\activate`
  ```
2. Install backend dependencies:
  ```
  pip install -r requirements.txt
  ```
3. Create a `.env` file and configure the required API keys:
   ```bash
   LLM_API_KEY=<your_openai_api_key>
   LLM_BASE_URL=<your_openai_base_url>
   LLM_MODEL=<your_model_name>
   MAX_ARTICLES=10
   ```
5. Run the FastAPI server:
   ```bash
   uvicorn api:app --reload
   ```

#### Frontend Setup

1. Navigate to the frontend folder and create a virtual environment:
  ```bash
    cd frontend
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
  ```
2. Install backend dependencies:
  ```
  pip install -r requirements.txt
  ```
3. Run the Streamlit UI:
   ```bash
   streamlit run app.py
   ```

---

## Model Details
### Summarization and Topic Extraction
- Uses an OpenAI LLM model to extract key topics and summarize articles.
- Ensures valid JSON response parsing from LLM output.

### Sentiment Analysis
- Uses `TextBlob` to analyze sentiment.
- Classifies sentiment as **Positive, Negative, or Neutral**.

### Comparative Analysis
- Compares sentiment across articles.
- Extracts key differences and common themes.

### Final Analysis
- Summarizes overall sentiment across all articles.

### Text-to-Speech (TTS)
- Uses `gTTS` to generate Hindi speech for the final sentiment analysis.

---

## API Development
The API is developed using FastAPI and includes the following endpoint:

### **GET /analyze-company-news**
Streams processed data, including:
- News fetching status
- Processed articles (title, summary, topics, sentiment)
- Comparative sentiment analysis
- Final sentiment assessment
- Hindi audio file URL

#### Example Request:
```bash
curl -X GET "http://localhost:8000/analyze-company-news?company=Tesla"
```
#### Example Response:
```json
{
  "articles": [
    {
      "title": "Tesla stocks surge",
      "summary": "Tesla reports record sales in Q1.",
      "topics": ["Stocks", "Sales"],
      "sentiment": "Positive",
      "url": "https://example.com/article"
    }
  ],
  "comparative_sentiment_score": {
    "sentiment_distribution": {
      "Positive": 6,
      "Negative": 2,
      "Neutral": 2
    },
    "coverage_differences": [
      {
        "comparison": "Article 1 emphasizes market growth, while Article 2 discusses legal challenges.",
        "impact": "Investors may react positively to the growth, but legal issues raise concerns."
      }
    ],
    "topic_overlap": ["topic1", "topic2"]
    
  },
  "final_sentiment_analysis": "Tesla’s latest news coverage is mostly positive. Potential stock growth expected.",
  "audio": "static/output.mp3"
}
```

---

## API Usage
### Third-Party APIs Used
- **Google Search** (Scraping news articles)
- **OpenAI** (Summarization and analysis)
- **gTTS** (Text-to-Speech conversion)
- **Google Translate** (English to Hindi translation)

---

## Assumptions & Limitations
- **Assumptions:**
  - Google News provides sufficient articles for analysis.
  - The LLM accurately extracts topics and sentiment.
- **Limitations:**
  - Some news pages may block scraping.
  - Sentiment analysis using `TextBlob` may be less accurate than deep learning models.
  - Hindi translation quality depends on Google Translate.
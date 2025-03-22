from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from get_news import get_google_news
from utils import extract_topics_and_summary, analyze_sentiment, comparative_analysis, final_analysis, generate_hindi_tts
import asyncio
import json
import os

app = FastAPI()

if not os.path.exists("static"):
    os.makedirs("static")
app.mount("/static", StaticFiles(directory="static"), name="static")

async def process_article(article):
    """Summarize, extract topics, and analyze sentiment asynchronously."""
    loop = asyncio.get_running_loop()

    topics_and_summary = await loop.run_in_executor(None, extract_topics_and_summary, article["content"])
    article["topics"] = topics_and_summary["topics"]
    article["summary"] = topics_and_summary["content"]

    article["sentiment"] = await loop.run_in_executor(None, analyze_sentiment, f"{article['title']}: {article['summary']}")
    return article

async def process_articles_parallel(articles):
    """Process all articles in parallel."""
    tasks = [process_article(article) for article in articles]
    return await asyncio.gather(*tasks)

async def stream_news_analysis(company: str):
    """Stream data as it's processed, sending each step separately."""
    yield json.dumps({"status": "fetching_news"}) + "\n"
    articles = get_google_news(company)

    if not articles:
        yield json.dumps({"error": "No valid articles found."}) + "\n"
        return

    yield json.dumps({"status": "processing_articles"}) + "\n"
    articles = await process_articles_parallel(articles)
    yield json.dumps({"articles": articles}) + "\n"

    yield json.dumps({"status": "running_analysis"}) + "\n"
    comparative_sentiment_summary, final_summary = await asyncio.gather(
        asyncio.to_thread(comparative_analysis, articles),
        asyncio.to_thread(final_analysis, articles)
    )
    yield json.dumps({"comparative_sentiment_score": comparative_sentiment_summary}) + "\n"
    yield json.dumps({"final_sentiment_analysis": final_summary}) + "\n"

    yield json.dumps({"status": "generating_audio"}) + "\n"
    audio_file = await generate_hindi_tts(final_summary)
    yield json.dumps({"audio": audio_file}) + "\n"

@app.get("/analyze-company-news", response_class=StreamingResponse)
async def analyze_company_news(company: str):
    return StreamingResponse(stream_news_analysis(company), media_type="application/json")

@app.get("/ping")
async def ping():
    return {"message": "pong"}
import json
import re
from textblob import TextBlob
from collections import Counter
from openai import OpenAI
from gtts import gTTS
from googletrans import Translator
from dotenv import load_dotenv
import os

load_dotenv()

# LLM Configuration
LLM_MODEL = os.getenv("LLM_MODEL")

client = OpenAI(
    api_key=os.getenv("LLM_API_KEY"),
    base_url=os.getenv("LLM_BASE_URL"),
)

class SentimentType:
    Positive = "Positive"
    Negative = "Negative"
    Neutral = "Neutral"

def response_to_dict(response):
    """Extract JSON data from LLM response."""
    try:
        match = re.search(r'(?P<json>\{.*\})', response.choices[0].message.content, re.DOTALL)
        return json.loads(match.group('json'))
    except:
        raise ValueError("No valid JSON found in the response content.")

def analyze_sentiment(text):
    """Perform sentiment analysis using TextBlob."""
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity
    if polarity > 0:
        return SentimentType.Positive
    elif polarity < 0:
        return SentimentType.Negative
    else:
        return SentimentType.Neutral

def extract_topics_and_summary(text):
    """Extract key topics and generate a summary using LLM."""
    prompt = '''
    Extract the key topics and generate a concise summary. Respond in JSON format, example:
    {
      "content": "Summarized text here",
      "topics": ["topic1", "topic2", "topic3"]
    }
    Article: ''' + text + "\n\nEnsure the response is **valid JSON** with no extra text before or after."

    response = client.chat.completions.create(
        model=LLM_MODEL,
        messages=[{"role": "user", "content": prompt}],
    )

    return response_to_dict(response)

def comparative_analysis(articles):
    """Compare sentiment across articles and extract key insights."""
    sentiment_counts = Counter(article['sentiment'] for article in articles)
    sentiment_distribution = {
        SentimentType.Positive: sentiment_counts[SentimentType.Positive],
        SentimentType.Negative: sentiment_counts[SentimentType.Negative],
        SentimentType.Neutral: sentiment_counts[SentimentType.Neutral],
    }
    
    combined_summaries = "\n\n".join(
        [f"Article {i+1}: {article['summary']}\nKey Topics: {', '.join(article['topics'])}" 
         for i, article in enumerate(articles)]
    )

    prompt = '''
    Compare the sentiment and key themes across multiple articles. Respond in JSON format, example:
    {
      "coverage_differences": [
        {
          "comparison": "Article 1 emphasizes market growth, while Article 2 discusses legal challenges.",
          "impact": "Investors may react positively to the growth, but legal issues raise concerns."
        }
      ],
      "topic_overlap": ["topic1", "topic2"]
    } 

    Articles: ''' + combined_summaries  + "\n\nEnsure the response is **valid JSON** with no extra text before or after."
    
    response = client.chat.completions.create(
        model=LLM_MODEL,
        messages=[{"role": "user", "content": prompt}],
    )

    analysis = response_to_dict(response)
    
    return {
        "sentiment_distribution": sentiment_distribution,
        "coverage_differences": analysis["coverage_differences"],
        "topic_overlap": analysis["topic_overlap"]
    }

def final_analysis(articles):
    """Generate a final sentiment summary across all articles."""
    combined_summaries = "\n\n".join([f"Article {i+1}: {article['summary']}" for i, article in enumerate(articles)])

    prompt = '''
    Provide a final analysis of the sentiment and coverage of these articles. Respond in JSON format, example:
    {
      "final_sentiment_analysis": "Tesla’s latest news coverage is mostly positive. Potential stock growth expected."
    }

    Articles: ''' + combined_summaries  + "\n\nEnsure the response is **valid JSON** with no extra text before or after."
    
    response = client.chat.completions.create(
        model=LLM_MODEL,
        messages=[{"role": "user", "content": prompt}],
    )

    return response_to_dict(response)["final_sentiment_analysis"]

async def generate_hindi_tts(text, filename="output.mp3"):
    """Convert summary text to Hindi speech and save as an audio file."""
    translator = Translator()
    text_to_translate = await translator.translate(text, src='en', dest='hi')
    translated_text = text_to_translate.text

    tts = gTTS(text=translated_text, lang='hi')
    path = "/static/" + filename
    tts.save(path)
    return path
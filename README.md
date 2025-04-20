# CBC Editorial Assistance - RAG Chatbot

This is a editorial chatbot for CBC internal documents and Json.This application is a lightweight RAG(Retrieval Augmented Generation)
designed to assist editorial staff by answering policy questions, Suggesting SEO-optimized headlines and summarizing articles for social media.

\_\_

## Setup Instructions

### Install Requirements

Ensure Python3.10+ is installed

```bash
pip install -r requirements.txt
python3 embadings,py # to create embadings to store in Faiss DB
streamlit run app.py # To run application for UI
```

## Technical Stack

Embading model = OpenAI embading model "text-embedding-3-large"
Model = OpenAI for response "GPT-4o-mini"
framework = Langchain
Vectoredatabase = Faiss

## Sample Test conversion

![Policy Question!]("policy Question.png")
![Headline Suggision!]("headline_suggision.png")
![Tweetsummary!]("tweet_summary.png")

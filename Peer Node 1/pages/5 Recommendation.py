import streamlit as st
import time
import requests
import openai
import streamlit as st
import praw
import itertools
import re
from collections import Counter
from nltk.sentiment import SentimentIntensityAnalyzer

st.title('Welcome to the Recommendation Page')

st.text('Here is where you can learn about new popular stocks.\n\n')


reddit = praw.Reddit(
    client_id='ANd8HyvVk9AQ8z7ngrq8Kw',
    client_secret='dCazES-EGzVBOMLTl4mszU1KrW790g',
    user_agent='StockFinder by /u/RoutineFickle8556',
    username='RoutineFickle8556'
)

def GPTExplanation(sentimentfromStock):
    # 
    openai.api_key = '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'

    openai.api_key = 'KEY'
    text = sentimentfromStock

    set_engine = 'gpt-3.5-turbo-1106'

    prompt = "Can you explain these sentiments for each stock?"

    completion = openai.Completion.create(

        engine = set_engine,
        prompt = prompt + text, 
        max_tokens = 1024,
        n = 1,
        stop = None,
        temperature = 0.5
    )

    response = completion.choices[0].text

    return response

#Top Stocks
def giveSentiment():
    subreddits = ["stocks", "investing", "wallstreetbets", "trading", "stockmarket"]


    with open('tickers.txt', 'r') as file:
        tickers = {line.strip() for line in file}
    sia = SentimentIntensityAnalyzer()
    sentiment_scores = {ticker: [] for ticker in tickers}

    for subreddit_name in subreddits:
        subreddit = reddit.subreddit(subreddit_name)
    time_last_week = time.time() - (7 * 24 * 60 * 60)
        
    for submission in subreddit.new(limit=None):
        if submission.created_utc < time_last_week:
            continue
        
        combined_text = (submission.title + " " + submission.selftext).upper()
        words = set(combined_text.split())
        found_tickers = words.intersection(tickers)
        
        for ticker in found_tickers:
            stock_mentions.update([ticker])
            sentiment_result = sia.polarity_scores(submission.title + " " + submission.selftext)
            sentiment_scores[ticker].append(sentiment_result['compound'])

    top_5_stocks = stock_mentions.most_common(5)
    sentimentScores = {}
    for stock, _ in top_5_stocks:
        average_sentiment = sum(sentiment_scores[stock]) / len(sentiment_scores[stock]) if sentiment_scores[stock] else 0
        sentimentScores[stock] = average_sentiment
    return sentimentScores



stock_mentions = Counter()

#Top stocks
def giveTopStocks():
    reddit = praw.Reddit(
    client_id='S1YTPi5slwsRq9H7SDrjSw',
    client_secret='vlfo49Jf8dHGRlPFUzNxRZvtRkSZMw',
    user_agent='StockFinder by /u/HoneydewSouth1689',
    username='HoneydewSouth1689'
    )

    subreddits = ["stocks", "investing", "wallstreetbets", "trading", "stockmarket"]


    with open('data/tickers.txt', 'r') as file:
        tickers = {line.strip() for line in file}

    time_last_week = time.time() - (7 * 24 * 60 * 60)

    for subreddit_name in subreddits:
        subreddit = reddit.subreddit(subreddit_name)
        
        for submission in subreddit.new(limit=None):
            if submission.created_utc < time_last_week:
                continue
            
            texts = [submission.title, submission.selftext]
            for text in texts:
                words = set(text.upper().split())
                found_tickers = words.intersection(tickers)
                stock_mentions.update(found_tickers)

    return stock_mentions.most_common(10)


#coMentions of Stocks
def coMention():
    def update_co_mentions(texts, tickers, co_mention_counts):
        combined_text = " ".join(texts).upper()
        words = set(combined_text.split())
        found_tickers = list(words.intersection(tickers))

        if len(found_tickers) > 1:
            for pair in itertools.combinations(sorted(found_tickers), 2):
                co_mention_counts.update([pair])

    subreddits = ["stocks", "investing", "wallstreetbets", "trading", "stockmarket"]

    with open('tickers.txt', 'r') as file:
        tickers = {line.strip() for line in file}

    time_last_week = time.time() - (7 * 24 * 60 * 60)

    stock_mentions = Counter()
    co_mention_counts = Counter()

    for subreddit_name in subreddits:
        subreddit = reddit.subreddit(subreddit_name)
        for submission in subreddit.new(limit=None):
            if submission.created_utc < time_last_week:
                continue

            texts = [submission.title, submission.selftext]
            
            words = set(" ".join(texts).upper().split())
            found_tickers = words.intersection(tickers)
            stock_mentions.update(found_tickers)

            update_co_mentions(texts, tickers, co_mention_counts)

    top_co_mentions = co_mention_counts.most_common(10)
    return top_co_mentions

if st.button('Give me popular stocks from Reddit!'):
    # This will be the format of the stocks!
    # popular_stocks = """
    # | Stock | Mentions |
    # | --- | --- |
    # | TSLA | 48 |
    # | SPY | 25 |
    # | NVDA | 19 |
    # | MSFT | 12 |
    # | BA | 10 |
    # | QQQ | 10 |
    # | AMD | 6 |
    # | GOOGL | 6 |
    # | INTC | 5 |
    # | T | 5 |
    # """
    st.markdown(giveTopStocks())
    
if st.button('Out of the given stocks, give me the most closely related Stocks!'):
    # This will be the format of the coMentions
    # "'BA' and 'TSLA' have been closely mentioned 6 times" 
    st.write(coMention())

stockSentiment = ""
if st.button('Give me the sentiment of these top Stocks!'):
    # Output will be of this format
    # sentiment_output = """
    # | Stock | Average Sentiment |
    # | --- | --- |
    # | TSLA | -0.12 |
    # | SPY | 0.04 |
    # | NVDA | 0.38 |
    # | MSFT | 0.14 |
    # | BA | -0.45 |
    # """
    st.markdown(giveSentiment())

if st.button('Explain sentiment'):
    # This is a mock GPT Output in the case the API does not function

    # text = "TSLA (Tesla Inc.): The sentiment for Tesla Inc. (TSLA) is 
    #slightly negative, with an average sentiment score of -0.12. This could 
    #indicate that recent news, discussions, or analyst opinions about the company 
    #have been somewhat unfavorable. However, it's important to note that sentiment 
    #scores can fluctuate over time and may not always reflect the company's long-term 
    #prospects. \n\nSPY (S&P 500 ETF): The S&P 500 ETF (SPY) has a slightly positive average 
    #sentiment score of 0.04. This could suggest that the overall sentiment towards the broader 
    #market, as represented by the S&P 500 index, has been relatively neutral or mildly positive 
    #recently. \n\nNVDA (NVIDIA Corporation): NVIDIA Corporation (NVDA) has a positive average 
    #sentiment score of 0.38, which indicates that the sentiment surrounding the company has 
    #been generally favorable. This could be due to positive news, analyst recommendations, or 
    #investor optimism about the company's performance or growth prospects. \n\nMSFT (Microsoft Corporation): 
    #Microsoft Corporation (MSFT) has a positive average sentiment score of 0.14, suggesting that the sentiment 
    #towards the company has been moderately positive. This could be attributed to 
    #factors such as strong financial performance, positive product releases, or favorable 
    #market conditions for the technology sector. \n\nBA (Boeing Company): The Boeing Company 
    #(BA) has a negative average sentiment score of -0.45, which indicates that the sentiment 
    #surrounding the company has been unfavorable. This could be due to various factors, such as 
    #negative news reports, financial challenges, or concerns about the company's products or operations."
    st.write(GPTExplanation(stockSentiment))





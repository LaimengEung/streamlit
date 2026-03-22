import streamlit as st
import pandas as pd
import plotly.express as px

# Set page config
st.set_page_config(             
    page_title="Airline Sentiment Dashboard",
    layout='wide'
)

# Load the data in cache
@st.cache_data
def load_data():
    df = pd.read_csv("Tweets.csv")
    df["tweet_created"] = pd.to_datetime(df['tweet_created'])
    return df

df = load_data()

# Header row
c1, c2 = st.columns([3, 1])     # creates 2 side-by-side columns with a 3:1 width ratio
with c1:
    st.title("Airline Sentiment Dashboard")
with c2: 
    st.caption("Simple Interactive Dashboard with Streamlit")

# Filters row
f1, f2, f3 = st.columns([0.35, 0.35, 0.3])
with f1:
    all_airlines = sorted(df["airline"].unique()) 
    airline_options = ['All'] + all_airlines        # Add a fake 'All' option (streamlit doesn't have a built-in all option)
    selected_airlines = st.multiselect("Airline", airline_options, default=['All'])
    if "All" in selected_airlines:
        selected_airlines_effective = all_airlines
    else:
        selected_airlines_effective = selected_airlines
with f2:
    sentiments = ['positive', 'neutral', 'negative']
    selected_sentiments = st.multiselect("Sentiment", sentiments, default=sentiments)
with f3:
    text_query = st.text_input("Keyword in tweet text", placeholder="e.g. delayed, thanks...")

# this will dynamically change (depending on the f1, f2, f3) 
filtered = df[
    df['airline'].isin(selected_airlines_effective) &
    df['airline_sentiment'].isin(selected_sentiments)
].copy()

# text query for text
if text_query.strip():
    filtered = filtered[filtered['text'].str.contains(text_query, case=False, na=False)]

# KPIs
k1, k2, k3, k4, k5 = st.columns(5)
total_tweets = len(filtered)
pos_count = (filtered['airline_sentiment'] == 'positive').sum()
neut_count = (filtered['airline_sentiment'] == 'neutral').sum()
neg_count = (filtered['airline_sentiment'] == 'negative').sum()
pos_rate = (pos_count / total_tweets * 100) if total_tweets else 0

with k1:
    st.metric("Total Tweets", f"{total_tweets:,}", border=True)
with k2:
    st.metric("Positive", f"{pos_count:,}", border=True)
with k3:
    st.metric("Neutral", f"{neut_count:,}", border=True)
with k4:    
    st.metric("Negative", f"{neg_count:,}", border=True)
with k5:
    st.metric("Positive Rate", f"{pos_rate:.1f}%", border=True)

# Charts row
ch1, ch2 = st.columns(2)

with ch1:
    st.subheader("Sentiment Distribution")
    sentiment_count = (
        filtered['airline_sentiment']
        .value_counts()
        .rename_axis("sentiment")       # names the index sentiment, so it becomes a proper column name
        .reset_index(name="tweets")     # coverts the Series into a DF with 2 columns: sentiment, tweets
    )
    fig_sent = px.bar(sentiment_count, x='sentiment', y='tweets', color='sentiment')
    st.plotly_chart(fig_sent)

with ch2:
    st.subheader("Tweets by Airline")
    airline_count = (
        filtered['airline']
        .value_counts()
        .rename_axis("airline")
        .reset_index(name='tweets')
    )
    fig_airline = px.bar(airline_count, x='airline', y='tweets', color='airline')
    st.plotly_chart(fig_airline)

# All raw data
st.subheader("Tweet Details")
st.dataframe(
    filtered[["tweet_created", "airline", "airline_sentiment", "text"]]
)
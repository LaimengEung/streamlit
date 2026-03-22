import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt         # use to turn off axes for wordcloud, not actual visualization

st.title('Sentiment Analysis of Tweets about US Airlines')
st.sidebar.title("Sentiment Analysis of Tweets about US Airlines")

st.markdown("This application is a streamlit dashboard to analyse the sentiment of Tweets 🥶")
st.sidebar.markdown("This application is a streamlit dashboard to analyse the sentiment of Tweets 🥶")

@st.cache_data() # cache, to save time and energy
def load_data(path):
    data = pd.read_csv(path)
    data['tweet_created'] = pd.to_datetime(data['tweet_created'])
    return data

# @st.cache_data for data loading, transformations, API calls
    # returns a new, independent copy of the cached data
# @st.cache_resource for ML models, DB connections, API clients
    # returns a pointer to the same, single object across all sessions

DATA_PATH = 'Tweets.csv'

data = load_data(DATA_PATH)

# st.write(data): display the whole data DF 

# Show Random Tweet Text
st.sidebar.subheader("Show random tweet")
random_tweet = st.sidebar.radio(
    label='Sentiment', 
    options=('positive', 'neutral', 'negative')
)
filtered_text = data.query('airline_sentiment == @random_tweet')['text'].sample(n=1).iat[0]
st.sidebar.markdown(filtered_text)

# Visualization for No. of Tweets by Sentiment
st.sidebar.markdown("### Number of tweets by sentiment")
select = st.sidebar.selectbox(
    label="Visualization",
    options=['Histogram', 'Pie chart'],
    key='no_tweet_by_sentiment'     # a unique key for this specific itme (selectbox)
)
sentiment_count = data['airline_sentiment'].value_counts()
sentiment_count = pd.DataFrame({
    'Sentiment': sentiment_count.index,
    'Tweets': sentiment_count.values})

    # Checkbox for show or not
if not st.sidebar.checkbox("Hide", True):
    st.markdown("### Number of tweets by sentiment")
    if select == 'Histogram':
        fig = px.histogram(sentiment_count, x='Sentiment', y='Tweets', color='Tweets', height=500)
        st.plotly_chart(fig)    # st function to display plotly charts
    else:
        fig = px.pie(sentiment_count, names='Sentiment', values='Tweets')
        st.plotly_chart(fig)

# Visualization of Map
    # All you need is the coordinate (lat, lon)
st.sidebar.subheader("When and where are users tweeting from?")
hour = st.sidebar.slider(
    label='Hour of day',
    min_value=0,
    max_value=23
)   # Other options include number_input...
modified_data = data[data['tweet_created'].dt.hour == hour]
if not st.sidebar.checkbox("Close", True, key='visualization_map'):
    st.markdown("### Tweets locations based on the time of day")
    st.markdown(f"{len(modified_data)} Tweets between {hour}:00 and {(hour+1)%24}:00")
    st.map(modified_data)
    if st.sidebar.checkbox("Show raw data", False): # False here is just initial/default value
        st.write(modified_data)                     # this still only returns if we check the checkbox

# Multi-Select
st.sidebar.subheader("Breakdown of airline tweets by sentiment")
choice = st.sidebar.multiselect(
    label='Pick airline',
    options=(sorted(data['airline'].unique())),
    key='multi-select_sentiment_by_airline'
)

if len(choice) > 0:    # only display chart when there is an option selected
    choice_data = data[data['airline'].isin(choice)]
    fig_choice = px.histogram(
        choice_data, 
        x='airline', 
        y='airline_sentiment',          # with histfunc, y is normally not neccessary!
        histfunc='count',               # tells plotly how to aggregate values inside each bin/group (it has count, sum, min, max...)
        color='airline_sentiment', 
        facet_col='airline_sentiment',  # splits one chart into multiple small subplots by a column (itc, creates seperate panels for pos, neut, neg)
        labels={'airline_sentiment': 'tweets'}, 
        height=600, width=800
    )
    st.plotly_chart(fig_choice)

# Word Cloud
st.sidebar.header("Word Cloud")
word_sentiment = st.sidebar.radio(
    label="Display word cloud for what sentiment",
    options=('positive', 'neutral', 'negative')
)

if not st.sidebar.checkbox("Close", True, key='word_cloud'):
    st.header(f"Word Cloud for {word_sentiment} sentiment")
    df = data[data['airline_sentiment'] == word_sentiment]
    words = ' '.join(df['text'])
    processed_words = ' '.join(
        [word for word in words.split() 
         if 'http' not in word and not word.startswith('@') and word != 'RT']
    )   # we don't want links, handles (@), or ReTweets

    # If we want to cache, we can also @st.cache_resource it, to preventing regenrating every rerun
    word_cloud = WordCloud(stopwords=STOPWORDS, height=640, width=800).generate(processed_words)

    fig_wc, ax = plt.subplots(figsize=(10, 8))
    ax.imshow(word_cloud, interpolation="bilinear")  # interpolation controls how pixels are smoothed (bilinear: smoother, softer edges)
    ax.axis("off")      # turn off axes for our wordcloud, it's basically an image
    st.pyplot(fig_wc)
    plt.close(fig_wc)   # important to prevent rerunning our fig_wc every time we rerun streamlit (saves memory)
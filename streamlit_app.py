import streamlit as st
from googleapiclient.discovery import build
#from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pandas as pd
import csv
import os
import pickle

# Assuming you've set up st.secrets["YOUTUBE_API_KEY"] and st.secrets["OPENAI_API_KEY"] in your Streamlit app's secrets
youtube_api_key = st.secrets["secrets"]["YOUTUBE_API_KEY"]
youtube = build('youtube', 'v3', developerKey=youtube_api_key)

def search_youtube(keyword):
    # This function searches YouTube for videos matching the keyword and returns a DataFrame with video IDs and titles
    request = youtube.search().list(q=keyword, part="id,snippet", maxResults=30, type="video")
    response = request.execute()

    videos = []
    for item in response.get('items', []):
        video_id = item['id']['videoId']
        title = item['snippet']['title']
        tags = item['items'][0]['snippet'].get('tags', [])
        videos.append({"video_id": video_id, "title": title, "tags": tags})

    return pd.DataFrame(videos)

def download_as_csv(dataframe):
    # This function converts a DataFrame to CSV and allows the user to download it
    csv = dataframe.to_csv(index=False)
    st.download_button(label="Download data as CSV", data=csv, file_name='youtube_data.csv', mime='text/csv')

def app_ui():
    st.title("YouTube Video Metadata Collector")
    keyword = st.text_input("Enter a keyword to search on YouTube:", "")

    if keyword and st.button("Search YouTube"):
        df = search_youtube(keyword)
        st.write(df)
        download_as_csv(df)

    # Placeholder for video file upload
    uploaded_video = st.file_uploader("Upload a video file:", type=["mp4"])
    if uploaded_video is not None:
        st.video(uploaded_video)

if __name__ == "__main__":
    app_ui()

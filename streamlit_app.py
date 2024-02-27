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
    request = youtube.search().list(q=keyword, part="id", maxResults=30, type="video")
    response = request.execute()

    video_ids = [item['id']['videoId'] for item in response.get('items', [])]
    videos_request = youtube.videos().list(id=','.join(video_ids), part="snippet")
    videos_response = videos_request.execute()

    videos_info = []
    for item in videos_response.get('items', []):
        video_id = item['id']
        title = item['snippet']['title']
        tags = item['snippet'].get('tags', [])
        
        videos_info.append({"video_id": video_id, "title": title, "tags": tags})

    return pd.DataFrame(videos_info)

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

def accumulate_tags(videos_response):
    all_tags = []
    for video in videos_response:
        tags = video.get("tags", [])
        all_tags.extend(tags)
    return list(set(all_tags))  # Remove duplicates by converting to a set and back to a list
    


if __name__ == "__main__":
    app_ui()

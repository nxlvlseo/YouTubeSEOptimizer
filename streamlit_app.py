import streamlit as st
from googleapiclient.discovery import build
#from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pandas as pd
import csv
import os
import pickle
import openai

# Initialize APIs
youtube_api_key = st.secrets["secrets"]["YOUTUBE_API_KEY"]
youtube = build('youtube', 'v3', developerKey=youtube_api_key)
openai.api_key = st.secrets["secrets"]["OPENAI_API_KEY"]


def search_youtube(keyword):
    request = youtube.search().list(q=keyword, part="id", maxResults=30, type="video")
    response = request.execute()
    video_ids = [item['id']['videoId'] for item in response.get('items', [])]
    videos_request = youtube.videos().list(id=','.join(video_ids), part="snippet")
    videos_response = videos_request.execute()
    videos_info = [{"video_id": item['id'], "title": item['snippet']['title'], "tags": item['snippet'].get('tags', [])} for item in videos_response.get('items', [])]
    return pd.DataFrame(videos_info)

def refine_tags_and_generate_comments(tags):
    # Join tags into a single string
    tags_str = ", ".join(tags)
    
    # Prepare the conversation prompts
    prompts = [
        {"role": "system", "content": "You are a knowledgeable YouTube assistant."},
        {"role": "user", "content": f"Refine and optimize these YouTube tags for better reach: {tags_str}."},
        {"role": "user", "content": "Generate 50 engaging YouTube comments based on these tags."}
    ]
    
    # Use the chat completion endpoint for a conversational model
    response = openai.ChatCompletion.create(
        model="gpt-4",  # Specify the chat model you're using
        messages=prompts,
        temperature=0.7,
        max_tokens=500,
    )
    
    # Assuming the last two messages in the response will be refined tags and generated comments
    refined_tags = response.choices[-2]['message']['content']
    comments = response.choices[-1]['message']['content']
    
    return refined_tags, comments

def app_ui():
    st.title("YouTube Video Metadata Collector")
    keyword = st.text_input("Enter a keyword to search on YouTube:", "")
    if keyword:
        if st.button("Search YouTube"):
            df = search_youtube(keyword)
            if not df.empty:
                st.write(df)
                all_tags = [tag for sublist in df['tags'].tolist() for tag in sublist if tag]
                unique_tags = list(set(all_tags))
                st.session_state['unique_tags'] = unique_tags

    if 'unique_tags' in st.session_state and st.button("Refine Tags and Generate Comments"):
        refined_tags, comments = refine_tags_and_generate_comments(st.session_state['unique_tags'])
        st.text_area("Refined Tags", value=refined_tags, height=100)
        st.text_area("Generated Comments", value=comments, height=300)
        combined_text = f"Refined Tags:\n{refined_tags}\n\nGenerated Comments:\n{comments}"
        st.download_button("Download Refined Tags and Comments", combined_text, "text/plain", "refined_tags_comments.txt")

if __name__ == "__main__":
    app_ui()

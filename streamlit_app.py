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
    tags_str = ", ".join(tags)
    try:
        # Initiate a chat session with OpenAI using a supported chat model
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an AI trained to refine video tags and generate engaging YouTube comments."},
                {"role": "user", "content": f"Refine these YouTube tags for better reach: {tags_str}."},
                {"role": "user", "content": "Generate 50 engaging YouTube comments based on these tags."}
            ]
        )
        
        # Initialize placeholders for the output
        # refined_tags, comments = "No refined tags generated.", "No comments generated."

        refined_tags = response['choices'][0]['message']['content'] if response['choices'] else "No refined tags generated."
        comments = response['choices'][1]['message']['content'] if len(response['choices']) > 1 else "No comments generated."

        return refined_tags, comments
    except Exception as e:
        st.error(f"An error occurred: {e}")
        return "Error", "Error"


def create_csv_content_for_download(refined_tags, comments):
    # Assuming refined_tags is a single string of comma-separated values
    tags_df = pd.DataFrame({'Refined Tags': refined_tags.split(',')})
    comments_df = pd.DataFrame({'Generated Comments': comments.split('\n')})  # Assuming comments are separated by newlines

    # Convert DataFrames to CSV
    tags_csv = tags_df.to_csv(index=False)
    comments_csv = comments_df.to_csv(index=False)
    
    return tags_csv, comments_csv


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
                
                if 'unique_tags' in st.session_state and st.button("Refine Tags and Generate Comments"):
                    refined_tags, comments = refine_tags_and_generate_comments(unique_tags)
                    st.text_area("Refined Tags", value=refined_tags, height=100)
                    st.text_area("Generated Comments", value=comments, height=300)
                    
                    # Prepare CSV content
                    tags_csv, comments_csv = create_csv_content_for_download(refined_tags, comments)
                    
                    # Download buttons for CSV files
                    st.download_button("Download Refined Tags CSV", tags_csv, "refined_tags.csv", "text/csv", key='download-tags')
                    st.download_button("Download Generated Comments CSV", comments_csv, "generated_comments.csv", "text/csv", key='download-comments')



if __name__ == "__main__":
    app_ui()

import streamlit as st
from googleapiclient.discovery import build
#from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pandas as pd
import csv
import os
import pickle
import openai

# Assuming you've set up st.secrets["YOUTUBE_API_KEY"] and st.secrets["OPENAI_API_KEY"] in your Streamlit app's secrets
youtube_api_key = st.secrets["secrets"]["YOUTUBE_API_KEY"]
youtube = build('youtube', 'v3', developerKey=youtube_api_key)
openai.api_key = st.secrets["secrets"]["OPENAI_API_KEY"]

def search_youtube(keyword):
    # Function to search YouTube and retrieve video IDs, titles, and tags
    request = youtube.search().list(q=keyword, part="id", maxResults=30, type="video")
    response = request.execute()

    video_ids = [item['id']['videoId'] for item in response.get('items', [])]
    videos_request = youtube.videos().list(id=','.join(video_ids), part="snippet")
    videos_response = videos_request.execute()

    videos_info = [{"video_id": item['id'], "title": item['snippet']['title'], "tags": item['snippet'].get('tags', [])} 
                   for item in videos_response.get('items', [])]

    return pd.DataFrame(videos_info)

def refine_tags_and_generate_comments(tags):
    # Function to refine tags and generate comments using OpenAI
    tags_str = ", ".join(tags)
    prompt_for_tags = f"Refine and optimize these YouTube tags for better reach: {tags_str}."
    prompt_for_comments = f"Generate 50 engaging YouTube comments based on these tags: {tags_str}."

    response_tags = openai.Completion.create(engine="text-davinci-003", prompt=prompt_for_tags, max_tokens=100, temperature=0.5)
    response_comments = openai.Completion.create(engine="text-davinci-003", prompt=prompt_for_comments, max_tokens=500, temperature=0.7, n=1, stop=["\n\n"])

    refined_tags = response_tags.choices[0].text.strip()
    comments = response_comments.choices[0].text.strip()

    return refined_tags, comments

def app_ui():
    st.title("YouTube Video Metadata Collector")
    keyword = st.text_input("Enter a keyword to search on YouTube:", "")

    if keyword:
        # Button to search YouTube and display results
        if st.button("Search YouTube"):
            df = search_youtube(keyword)
            if not df.empty:
                st.write(df)
                # Accumulate all tags from search results for processing
                all_tags = [tag for sublist in df['tags'].tolist() for tag in sublist]
                unique_tags = list(set(all_tags))  # Deduplicate tags

                # Button to refine tags and generate comments
                if st.button("Refine Tags and Generate Comments"):
                    refined_tags, comments = refine_tags_and_generate_comments(unique_tags)
                    st.text_area("Refined Tags", value=refined_tags, height=100)
                    st.text_area("Generated Comments", value=comments, height=300)
                    
                    # Option to download refined tags and comments
                    download_refined_tags_and_comments(refined_tags, comments)
                                    
                    
            else:
                st.write("No videos found.")

def download_refined_tags_and_comments(refined_tags, comments):
    combined_text = f"Refined Tags:\n{refined_tags}\n\nGenerated Comments:\n{comments}"
    st.download_button("Download Refined Tags and Comments", combined_text, "text/plain", "refined_tags_comments.txt")

def download_as_csv(dataframe):
    # This function converts a DataFrame to CSV and allows the user to download it
    csv = dataframe.to_csv(index=False)
    st.download_button(label="Download data as CSV", data=csv, file_name='youtube_data.csv', mime='text/csv')

if __name__ == "__main__":
    app_ui()

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
        #download_as_csv(df)

def accumulate_tags(videos_info):
    all_tags = []
    for video in videos_info:
        tags = video.get("tags", [])
        all_tags.extend(tags)
    return list(set(all_tags))  # Remove duplicates by converting to a set and back to a list
    
def refine_tags_and_generate_comments(tags):
    openai.api_key = st.secrets["secrets"]["OPENAI_API_KEY"]
    
    # Join tags into a single string
    tags_str = ", ".join(tags)
    prompt_for_tags = f"Refine and optimize these YouTube tags for better reach: {tags_str}."
    prompt_for_comments = f"Generate 50 engaging YouTube comments based on these tags: {tags_str}."
    
    # Deduplicate and optimize tags
    response_tags = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt_for_tags,
        max_tokens=100,
        temperature=0.5,
    )
    
    refined_tags = response_tags.choices[0].text.strip()
    
    # Generate comments
    response_comments = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt_for_comments,
        max_tokens=500,
        temperature=0.7,
        n=1,  # Adjust based on how many sets of comments you want
        stop=["\n\n"]  # Use stop sequences to control the length of each comment
    )
    
    comments = response_comments.choices[0].text.strip()
    
    return refined_tags, comments

def download_refined_tags_and_comments(refined_tags, comments):
    # Combine the tags and comments into a single string for download
    combined_text = f"Refined Tags:\n{refined_tags}\n\nGenerated Comments:\n{comments}"
    st.download_button("Download Refined Tags and Comments", combined_text, "text/plain", "refined_tags_comments.txt")


    if keyword and st.button("Search YouTube"):
        df = search_youtube(keyword)
        if not df.empty:
            all_tags = accumulate_tags(df.to_dict('records'))
            refined_tags, comments = refine_tags_and_generate_comments(all_tags)
            st.text_area("Refined Tags", value=refined_tags, height=100)
            st.text_area("Generated Comments", value=comments, height=300)
            download_refined_tags_and_comments(refined_tags, comments)
        else:
            st.write("No videos found.")


if __name__ == "__main__":
    app_ui()

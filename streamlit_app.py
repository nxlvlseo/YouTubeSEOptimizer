import streamlit as st
from googleapiclient.discovery import build
import pandas as pd
from moviepy.editor import VideoFileClip
import io

# Initialize YouTube client with your API key
youtube = build('youtube', 'v3', developerKey='YOUR_YOUTUBE_API_KEY')

def fetch_youtube_data(keyword):
    request = youtube.search().list(
        q=keyword,
        part="snippet",
        maxResults=30,
        type="video"
    )
    response = request.execute()
    
    # Extract video IDs to fetch comments and tags
    video_ids = [item['id']['videoId'] for item in response['items']]
    
    # Placeholder for your data collection
    data = {
        "keywords": [],
        "comments": [],
        "tags": []
    }
    
    # Loop through video IDs to fetch comments and tags
    for video_id in video_ids:
        # Fetch video details for tags
        video_request = youtube.videos().list(
            part="snippet",
            id=video_id
        )
        video_response = video_request.execute()
        video_tags = video_response['items'][0]['snippet']['tags'] if 'tags' in video_response['items'][0]['snippet'] else []
        data['tags'].extend(video_tags)
        
        # Fetch comments
        comments_request = youtube.commentThreads().list(
            part="snippet",
            videoId=video_id,
            maxResults=20  # Adjust as needed
        )
        comments_response = comments_request.execute()
        for item in comments_response['items']:
            comment = item['snippet']['topLevelComment']['snippet']['textDisplay']
            data['comments'].append(comment)
    
    # Assuming 'keyword' is also a keyword to be included
    data['keywords'].append(keyword)
    
    # Remove duplicates
    data['keywords'] = list(set(data['keywords']))
    data['tags'] = list(set(data['tags']))
    
    return data

def download_video_data(data):
    # Convert data to DataFrame for easy CSV download
    df = pd.DataFrame(data)
    return df.to_csv().encode('utf-8')

def main():
    st.title('YouTube Data Fetcher')

    keyword = st.text_input('Enter a keyword to search on YouTube:')
    
    if st.button('Fetch YouTube Data'):
        data = fetch_youtube_data(keyword)
        csv = download_video_data(data)
        st.download_button(
            label="Download data as CSV",
            data=csv,
            file_name='youtube_data.csv',
            mime='text/csv',
        )

if __name__ == "__main__":
    main()

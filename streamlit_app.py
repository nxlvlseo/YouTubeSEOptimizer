import streamlit as st
from googleapiclient.discovery import build
import pandas as pd

# Initialize YouTube client with your API key
youtube = build('youtube', 'v3', developerKey='YOUR_API_KEY')

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
    
    tags = []
    
    for video_id in video_ids:
        video_request = youtube.videos().list(part="snippet", id=video_id)
        video_response = video_request.execute()
        video_tags = video_response['items'][0]['snippet']['tags'] if 'tags' in video_response['items'][0]['snippet'] else []
        tags.extend(video_tags)
    
    # Remove duplicates
    unique_tags = list(set(tags))
    
    # Create a simple DataFrame with a single column for tags
    df = pd.DataFrame(unique_tags, columns=['Tags'])
    
    return df

def main():
    st.title('YouTube Data Fetcher')

    keyword = st.text_input('Enter a keyword to search on YouTube:')
    
    if st.button('Fetch YouTube Data'):
        df = fetch_youtube_data(keyword)
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download tags as CSV",
            data=csv,
            file_name='youtube_tags.csv',
            mime='text/csv',
        )

if __name__ == "__main__":
    main()

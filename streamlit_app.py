import streamlit as st
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
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
        videos.append({"video_id": video_id, "title": title})

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

# This is a simplified version and needs to be adjusted according to your authentication flow and stored credentials.
def authenticate_youtube():
    credentials = None
    # Token.pickle stores the user's credentials from previously successful logins
    if os.path.exists('token.pickle'):
        print("Loading Credentials From File...")
        with open('token.pickle', 'rb') as token:
            credentials = pickle.load(token)

    # If there are no valid credentials available, then either refresh the token or log in.
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            print("Refreshing Access Token...")
            credentials.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'client_secrets.json',
                scopes=['https://www.googleapis.com/auth/youtube.force-ssl']
            )
            flow.run_local_server(port=8080, prompt='consent', authorization_prompt_message='')
            credentials = flow.credentials
            # Save the credentials for the next run
            with open('token.pickle', 'wb') as f:
                print("Saving Credentials for Future Use...")
                pickle.dump(credentials, f)

    youtube = build('youtube', 'v3', credentials=credentials)
    return youtube

# Function to update video details
def update_video_details(youtube, video_id, tags, description):
    # Example of updating video's tags and description
    youtube.videos().update(
        part="snippet",
        body={
            "id": video_id,
            "snippet": {
                "tags": tags,
                "description": description
            }
        }
    ).execute()

if __name__ == "__main__":
    app_ui()

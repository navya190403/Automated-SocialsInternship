import streamlit as st
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.errors import HttpError, ResumableUploadError
from googleapiclient.http import MediaFileUpload
import os
import pickle
import socket
from dotenv import load_dotenv

class YouTubeOperations:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv('AIzaSyD4WotYONF7bOTtwFsm1sVUVYWVRrfuf8')  # Make sure the API_KEY is stored in .env file
        self.credentials = None
        self.youtube = None
        self.channel_id = None
        self.SCOPES = [
            'https://www.googleapis.com/auth/youtube.force-ssl',
            'https://www.googleapis.com/auth/youtube'
        ]

    def find_available_port(self, start_port=8501, max_attempts=100):
        for port in range(start_port, start_port + max_attempts):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind(('localhost', port))
                    return port
            except OSError:
                continue
        raise RuntimeError("Could not find an available port")

    def verify_youtube_channel(self):
        try:
            channels_response = self.youtube.channels().list(
                part='id,snippet',
                mine=True
            ).execute()

            if not channels_response.get('items'):
                st.error("No YouTube channel found for this Google account!")
                return False

            self.channel_id = channels_response['items'][0]['id']
            channel_title = channels_response['items'][0]['snippet']['title']
            st.success(f"Connected to YouTube channel: {channel_title}")
            return True

        except HttpError as e:
            st.error(f"Error verifying YouTube channel: {e}")
            return False

    def authenticate(self):
        try:
            if os.path.exists('token.pickle'):
                with open('token.pickle', 'rb') as token:
                    self.credentials = pickle.load(token)

            if not self.credentials or not self.credentials.valid:
                if self.credentials and self.credentials.expired and self.credentials.refresh_token:
                    st.info("Refreshing expired credentials...")
                    self.credentials.refresh(Request())
                else:
                    st.info("Starting new authentication flow...")
                    port = self.find_available_port()
                    flow = InstalledAppFlow.from_client_secrets_file(
                        'client_secrets.json',
                        self.SCOPES
                    )
                    self.credentials = flow.run_local_server(port=port)

                with open('token.pickle', 'wb') as token:
                    pickle.dump(self.credentials, token)
                st.success("Credentials saved successfully!")

            self.youtube = build('youtube', 'v3', credentials=self.credentials)
            st.success("YouTube API client created successfully!")
            
            if not self.verify_youtube_channel():
                raise Exception("YouTube channel verification failed")
                
            return self.youtube

        except Exception as e:
            st.error(f"Authentication error: {e}")
            raise

    def create_video(self, title, description, privacy_status, file_path):
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"Video file not found: {file_path}")

            body = {
                'snippet': {
                    'title': title,
                    'description': description,
                    'tags': ['API Test'],
                    'categoryId': '22'
                },
                'status': {
                    'privacyStatus': privacy_status,
                    'selfDeclaredMadeForKids': False,
                }
            }

            media = MediaFileUpload(
                file_path,
                chunksize=1024*1024,
                resumable=True
            )

            st.info("Starting video upload...")
            request = self.youtube.videos().insert(
                part=','.join(body.keys()),
                body=body,
                media_body=media
            )

            response = None
            while response is None:
                status, response = request.next_chunk()
                if status:
                    st.text(f"Uploaded {int(status.progress() * 100)}%")

            st.success(f"Video upload completed successfully! Video ID: {response['id']}")
            return response

        except ResumableUploadError as e:
            st.error(f"Upload error: {e}")
            raise
        except Exception as e:
            st.error(f"Unexpected error during video upload: {e}")
            raise

    def read_video(self, video_id):
        try:
            request = self.youtube.videos().list(
                part="snippet,contentDetails,statistics",
                id=video_id
            )
            response = request.execute()
            return response
        except Exception as e:
            st.error(f"Error reading video details: {e}")
            raise

    def update_video(self, video_id, title=None, description=None):
        try:
            video = self.youtube.videos().list(part="snippet", id=video_id).execute()
            if not video['items']:
                raise ValueError('Video not found')

            snippet = video['items'][0]['snippet']
            if title:
                snippet['title'] = title
            if description:
                snippet['description'] = description

            request = self.youtube.videos().update(
                part="snippet", body={"id": video_id, "snippet": snippet}
            )
            response = request.execute()
            return response

        except HttpError as e:
            st.error(f"Error updating video: {e}")
            raise
        except Exception as e:
            st.error(f"Unexpected error while updating video: {e}")
            raise

    def delete_video(self, video_id):
        try:
            request = self.youtube.videos().delete(id=video_id)
            request.execute()
            st.success("Video deleted successfully!")
            return True
        except Exception as e:
            st.error(f"Error deleting video: {e}")
            raise

    def list_my_videos(self, max_results=10):
        try:
            request = self.youtube.search().list(
                part="snippet", forMine=True, type="video", maxResults=max_results
            )
            response = request.execute()
            return response
        except Exception as e:
            st.error(f"Error listing videos: {e}")
            raise

    def display_menu(self):
        st.title("YouTube Operations Menu")
        option = st.selectbox(
            "Choose an option",
            ("Create Video", "Read Video", "Update Video", "Delete Video", "List My Videos")
        )

        if option == "Create Video":
            self.create_video_prompt()
        elif option == "Read Video":
            self.read_video_prompt()
        elif option == "Update Video":
            self.update_video_prompt()
        elif option == "Delete Video":
            self.delete_video_prompt()
        elif option == "List My Videos":
            self.list_videos_prompt()

    def create_video_prompt(self):
        title = st.text_input("Enter video title:")
        description = st.text_area("Enter video description:")
        privacy_status = st.selectbox("Enter privacy status:", ["public", "private", "unlisted"])
        file_path = st.file_uploader("Choose a video file to upload", type=["mp4", "avi", "mov"])
        
        if st.button("Upload Video"):
            if file_path is not None:
                with open(file_path.name, "wb") as f:
                    f.write(file_path.getbuffer())
                self.create_video(title, description, privacy_status, file_path.name)

    def read_video_prompt(self):
        video_id = st.text_input("Enter video ID to read details:")
        if st.button("Read Video"):
            if video_id:
                video_details = self.read_video(video_id)
                st.write(f"Video Details: {video_details}")

    def update_video_prompt(self):
        video_id = st.text_input("Enter video ID to update:")
        title = st.text_input("Enter new title (leave blank to skip):")
        description = st.text_area("Enter new description (leave blank to skip):")
        if st.button("Update Video"):
            if video_id:
                response = self.update_video(video_id, title, description)
                st.write(f"Updated video: {response}")

    def delete_video_prompt(self):
        video_id = st.text_input("Enter video ID to delete:")
        if st.button("Delete Video"):
            if video_id:
                self.delete_video(video_id)

    def list_videos_prompt(self):
        max_results = st.number_input("Enter the maximum number of videos to list:", min_value=1, max_value=50, value=10)
        if st.button("List My Videos"):
            videos = self.list_my_videos(max_results)
            st.write("Video list:")
            for video in videos.get('items', []):
                st.write(f"- {video['snippet']['title']} (ID: {video['id']})")

if __name__ == "__main__":
    youtube_operations = YouTubeOperations()
    youtube_operations.authenticate()
    youtube_operations.display_menu()


import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
import google.generativeai as genai
from google.generativeai import GenerativeModel, configure
import re
import os
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound, VideoUnavailable


# Load API key
from dotenv import load_dotenv
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

# Configure GenAI client or stop if missing
if not api_key:
    st.error("Missing GOOGLE_API_KEY. Add it to a .env file or environment and restart.")
    st.stop()
else:
    configure(api_key=api_key)


def get_video_id(url):
    """
    Extracts the video ID from various YouTube URL formats:
    - https://www.youtube.com/watch?v=VIDEO_ID
    - https://youtu.be/VIDEO_ID
    - https://www.youtube.com/live/VIDEO_ID
    """
    match = re.search(
        r"(?:v=|youtu\.be/|live/)([a-zA-Z0-9_-]{11})", 
        url
    )
    return match.group(1) if match else None


st.title("🎥 YouTube Video Summarizer (Gemini + Streamlit)")

url = st.text_input("Enter YouTube Video URL:")

if st.button("Summarize"):
    try:
        video_id = get_video_id(url)
        if video_id:
            st.info("⏳ Fetching transcript... please wait.")

            try:
                # Try fetching the transcript
                transcript = YouTubeTranscriptApi().fetch(video_id)
                text = " ".join([t.text for t in transcript])

            except (TranscriptsDisabled, NoTranscriptFound):
                st.error("⚠️ No transcript available for this video. Try another one.")
                st.stop()

            except VideoUnavailable:
                st.error("🚫 The video is unavailable or private.")
                st.stop()


            # Summarize with Gemini
            st.info("✨ Generating summary using Gemini 2.5 Flash...")
            model = GenerativeModel("gemini-2.5-flash")

            prompt = f"Summarize the following YouTube transcript into concise bullet points:\n{text}"
            response = model.generate_content(prompt)

            st.subheader("🧠 Summary")
            st.write(response.text)

        else:
            st.warning("⚠️ Please enter a valid YouTube URL.")

    except Exception as e:
        st.error(f"❌ Error: {e}")

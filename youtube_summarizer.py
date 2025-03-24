import requests
import json
import os
import argparse
from openai import OpenAI

def get_video_transcript(video_id, api_key):
    """
    Fetch the transcript of a YouTube video using SearchAPI.io
    """
    url = "https://www.searchapi.io/api/v1/search"
    params = {
        "engine": "youtube_transcripts",
        "video_id": video_id,
        "api_key": api_key
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # Raise an exception for HTTP errors
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching transcript: {e}")
        return None

def process_transcript(transcript_data):
    """
    Process the transcript data to create a single text
    """
    if not transcript_data or 'transcripts' not in transcript_data:
        return "No transcript available."
    
    full_transcript = ""
    for segment in transcript_data['transcripts']:
        full_transcript += segment['text'] + " "
    
    return full_transcript.strip()

def summarize_with_gpt4(transcript_text, openai_api_key):
    """
    Summarize the transcript using OpenAI's GPT-4 model
    """
    client = OpenAI(api_key=openai_api_key)
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o",  # Using gpt-4o model
            messages=[
                {"role": "system", "content": "You are a helpful assistant that creates concise bullet point summaries of video transcripts."},
                {"role": "user", "content": f"Please summarize the following YouTube video transcript into key bullet points, focusing on the main ideas and important details:\n\n{transcript_text}"}
            ],
            max_tokens=500
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error generating summary: {e}")
        return "Failed to generate summary."

def main():
    parser = argparse.ArgumentParser(description='Summarize YouTube videos into bullet points')
    parser.add_argument('--video_id', type=str, help='YouTube video ID')
    parser.add_argument('--searchapi_key', type=str, help='SearchAPI.io API key')
    parser.add_argument('--openai_key', type=str, help='OpenAI API key')
    
    args = parser.parse_args()
    
    # Use arguments or environment variables or default values
    video_id = args.video_id or os.environ.get('YOUTUBE_VIDEO_ID')
    searchapi_key = args.searchapi_key or os.environ.get('SEARCHAPI_KEY')
    openai_key = args.openai_key or os.environ.get('OPENAI_API_KEY')
    
    if not video_id:
        video_id = input("Enter YouTube video ID: ")
    
    if not searchapi_key:
        searchapi_key = input("Enter SearchAPI.io API key: ")
    
    if not openai_key:
        openai_key = input("Enter OpenAI API key: ")
    
    print(f"Fetching transcript for video ID: {video_id}...")
    transcript_data = get_video_transcript(video_id, searchapi_key)
    
    if transcript_data:
        print("Transcript fetched successfully!")
        full_transcript = process_transcript(transcript_data)
        
        print("Generating summary...")
        summary = summarize_with_gpt4(full_transcript, openai_key)
        
        print("\n--- VIDEO SUMMARY ---\n")
        print(summary)
        print("\n--------------------\n")
    else:
        print("Failed to retrieve transcript. Please check the video ID and API key.")

if __name__ == "__main__":
    main()
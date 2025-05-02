import streamlit as st
import pandas as pd
import requests
import re

st.title('TikTok Video Engagement Calculator')

st.write("""
Enter one or more TikTok video URLs (one per line). The app will fetch stats for each video and calculate engagement rates.
""")

# User input for TikTok URLs
urls_input = st.text_area("Enter TikTok video URLs:", height=200)

# Function to extract video ID from TikTok URL
def extract_video_id(url):
    match = re.search(r'/video/(\d+)', url)
    if match:
        return match.group(1)
    return url.rstrip('/').split('/')[-1]

# Function to fetch video data from RapidAPI
@st.cache_data(show_spinner=False)
def get_video_data(video_url, video_id):
    url = "https://tiktok-scraper2.p.rapidapi.com/video/info_v2"
    querystring = {"video_url": video_url, "video_id": video_id}
    headers = {
        "x-rapidapi-key": "2ddac25787msh88fa101b3b8f999p1663efjsn644bd80c24c9",
        "x-rapidapi-host": "tiktok-scraper2.p.rapidapi.com"
    }
    try:
        response = requests.get(url, headers=headers, params=querystring, timeout=10)
        data = response.json()
        if 'itemInfo' in data and 'itemStruct' in data['itemInfo']:
            item = data['itemInfo']['itemStruct']
            username = item.get('author', {}).get('uniqueId', 'Unknown')
            cover_url = item.get("video", {}).get("cover", "")
            stats = item.get('stats', {})
            likes = stats.get("diggCount", 0)
            views = stats.get("playCount", 0)
            comments = stats.get("commentCount", 0)
            shares = stats.get("shareCount", 0)
            engagement_rate = ((likes + comments + shares) / views) * 100 if views > 0 else 0
            return {
                "Username": username,
                "Views": views,
                "Likes": likes,
                "Comments": comments,
                "Shares": shares,
                "Engagement Rate": engagement_rate,
                "Cover URL": cover_url,
                "Video URL": video_url
            }
        else:
            # Show the API response for debugging
            st.warning(f"API response for {video_url}: {data}")
            return None
    except Exception as e:
        st.error(f"Error fetching data for {video_url}: {e}")
        return None

if st.button("Process URLs"):
    if urls_input:
        video_urls = [u.strip() for u in urls_input.splitlines() if u.strip()]
        video_data = []
        with st.spinner("Fetching video data..."):
            for url in video_urls:
                video_id = extract_video_id(url)
                data = get_video_data(url, video_id)
                if data:
                    video_data.append(data)
        if video_data:
            df = pd.DataFrame(video_data)
            df['Engagement Rate'] = pd.to_numeric(df['Engagement Rate'], errors='coerce')
            df['Engagement Rate (%)'] = df['Engagement Rate'].apply(lambda x: f"{round(x, 2)}%")
            st.write("### Video Details")
            st.dataframe(df[["Username", "Video URL", "Views", "Likes", "Comments", "Shares", "Engagement Rate (%)"]])
            # Totals
            st.write("### Total Statistics")
            st.dataframe(pd.DataFrame([df[["Views", "Likes", "Comments", "Shares"]].sum()]))
            # Averages
            st.write("### Average Statistics")
            st.dataframe(pd.DataFrame([df[["Views", "Likes", "Comments", "Shares", "Engagement Rate"]].mean().round(2)]))
        else:
            st.error("No valid data found for the entered videos.")
    else:
        st.warning("Please enter at least one TikTok video URL.") 
import os
import json
from datetime import datetime
import requests
from dotenv import load_dotenv

load_dotenv()

def format_timestamp(timestamp):
    """Convert ISO timestamp to readable format"""
    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
    return dt.strftime('%B %d, %Y at %I:%M %p')

def get_business_account_id(access_token, page_id):
    """Get the Instagram business account ID associated with a Facebook page"""
    url = f"https://graph.facebook.com/v18.0/{page_id}"
    params = {
        'fields': 'instagram_business_account{id,username}',
        'access_token': access_token
    }
    
    response = requests.get(url, params=params)
    if response.status_code != 200:
        print(f"Error getting business account: {response.text}")
        return None
        
    data = response.json()
    if 'instagram_business_account' in data:
        return data['instagram_business_account']['id']
    return None

def get_recent_posts(access_token, business_account_id, limit=10):
    """Fetch recent posts from Instagram"""
    url = f"https://graph.facebook.com/v18.0/{business_account_id}/media"
    params = {
        'fields': 'id,caption,media_type,media_url,permalink,thumbnail_url,timestamp,like_count,comments_count',
        'limit': limit,
        'access_token': access_token
    }
    
    response = requests.get(url, params=params)
    if response.status_code != 200:
        print(f"Error fetching posts: {response.text}")
        return None
        
    return response.json().get('data', [])

def main():
    # Get credentials from environment
    access_token = os.getenv("LONG_ACCESS_TOKEN")
    page_id = os.getenv("FACEBOOK_PAGE_ID")  # This should be your Facebook page ID
    
    if not access_token or not page_id:
        print("Error: Missing required environment variables.")
        print("Please set LONG_ACCESS_TOKEN and FACEBOOK_PAGE_ID in your .env file")
        return
    
    # First get the business account ID
    business_account_id = get_business_account_id(access_token, page_id)
    if not business_account_id:
        print("Could not find Instagram business account. Make sure:")
        print("1. The Facebook page is published")
        print("2. The page is connected to an Instagram business account")
        print("3. You have admin access to the page")
        return
    
    print(f"Found Instagram business account ID: {business_account_id}")
    
    # Fetch recent posts
    posts = get_recent_posts(access_token, business_account_id)
    if not posts:
        print("No posts found or error occurred")
        return
    
    # Display posts
    print(f"\nFound {len(posts)} recent posts:\n")
    for i, post in enumerate(posts, 1):
        print(f"Post {i}:")
        print(f"  Posted: {format_timestamp(post['timestamp'])}")
        print(f"  Type: {post['media_type']}")
        if 'caption' in post:
            caption = post['caption'][:100] + '...' if len(post['caption']) > 100 else post['caption']
            print(f"  Caption: {caption}")
        print(f"  Likes: {post.get('like_count', 0)}")
        print(f"  Comments: {post.get('comments_count', 0)}")
        print(f"  Link: {post['permalink']}")
        print()

if __name__ == "__main__":
    main() 
import requests
from typing import Dict, List, Optional, Union
import json

class InstagramAPI:
    def __init__(self, access_token: str, instagram_account_id: str):
        self.access_token = access_token
        self.instagram_account_id = instagram_account_id
        self.base_url = "https://graph.facebook.com/v18.0"
    
    def get_account_info(self) -> Optional[Dict]:
        """Get basic information about the Instagram business account"""
        url = f"{self.base_url}/{self.instagram_account_id}"
        params = {
            'fields': 'id,username,profile_picture_url,followers_count,media_count',
            'access_token': self.access_token
        }
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return response.json()
        print(f"Error getting account info: {response.text}")
        return None
    
    def get_media(self, limit: int = 25) -> Optional[List[Dict]]:
        """Get recent media (posts) from the Instagram account"""
        url = f"{self.base_url}/{self.instagram_account_id}/media"
        params = {
            'fields': 'id,caption,media_type,media_url,permalink,thumbnail_url,timestamp,like_count,comments_count',
            'limit': limit,
            'access_token': self.access_token
        }
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return response.json().get('data', [])
        print(f"Error getting media: {response.text}")
        return None
    
    def create_media(self, image_url: str, caption: str) -> Optional[str]:
        """Create a new media container (first step in posting)"""
        url = f"{self.base_url}/{self.instagram_account_id}/media"
        params = {
            'image_url': image_url,
            'caption': caption,
            'access_token': self.access_token
        }
        response = requests.post(url, params=params)
        if response.status_code == 200:
            return response.json().get('id')
        print(f"Error creating media: {response.text}")
        return None
    
    def publish_media(self, creation_id: str) -> Optional[str]:
        """Publish a previously created media container"""
        url = f"{self.base_url}/{self.instagram_account_id}/media_publish"
        params = {
            'creation_id': creation_id,
            'access_token': self.access_token
        }
        response = requests.post(url, params=params)
        if response.status_code == 200:
            return response.json().get('id')
        print(f"Error publishing media: {response.text}")
        return None
    
    def get_insights(self, metric: str = 'impressions', period: str = 'day') -> Optional[Dict]:
        """Get insights for the Instagram account"""
        url = f"{self.base_url}/{self.instagram_account_id}/insights"
        params = {
            'metric': metric,
            'period': period,
            'access_token': self.access_token
        }
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return response.json()
        print(f"Error getting insights: {response.text}")
        return None
    
    def get_comments(self, media_id: str) -> Optional[List[Dict]]:
        """Get comments for a specific media post"""
        url = f"{self.base_url}/{media_id}/comments"
        params = {
            'fields': 'id,text,username,timestamp,like_count',
            'access_token': self.access_token
        }
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return response.json().get('data', [])
        print(f"Error getting comments: {response.text}")
        return None
    
    def reply_to_comment(self, comment_id: str, message: str) -> Optional[str]:
        """Reply to a specific comment"""
        url = f"{self.base_url}/{comment_id}/replies"
        params = {
            'message': message,
            'access_token': self.access_token
        }
        response = requests.post(url, params=params)
        if response.status_code == 200:
            return response.json().get('id')
        print(f"Error replying to comment: {response.text}")
        return None

# Example usage:
if __name__ == "__main__":
    # Replace these with your actual values
    ACCESS_TOKEN = "your_long_lived_access_token"
    INSTAGRAM_ACCOUNT_ID = "your_instagram_business_account_id"
    
    # Initialize the API
    api = InstagramAPI(ACCESS_TOKEN, INSTAGRAM_ACCOUNT_ID)
    
    # Get account info
    account_info = api.get_account_info()
    if account_info:
        print(f"Account Info: {json.dumps(account_info, indent=2)}")
    
    # Get recent posts
    media = api.get_media(limit=5)
    if media:
        print(f"\nRecent Posts: {json.dumps(media, indent=2)}")
    
    # Get insights
    insights = api.get_insights()
    if insights:
        print(f"\nInsights: {json.dumps(insights, indent=2)}") 
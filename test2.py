import requests
import webbrowser
from urllib.parse import urlencode
import http.server
import socketserver
import threading
import urllib.parse
import json
import time
import os
import dotenv

dotenv.load_dotenv()

class InstagramAuth:
    def __init__(self, app_id, app_secret, redirect_uri, scopes=None):
        self.app_id = app_id
        self.app_secret = app_secret
        self.redirect_uri = redirect_uri
        self.auth_code = None
        self.access_token = None
        self.long_lived_token = None
        
        # Default scopes if none provided
        self.scopes = scopes or [
            'instagram_basic',
            'instagram_manage_comments',
            'pages_read_engagement',
            'pages_show_list'
        ]
    
    def get_auth_url(self):
        """Generate the authorization URL for user to grant permissions"""
        params = {
            'client_id': self.app_id,
            'redirect_uri': self.redirect_uri,
            'scope': ','.join(self.scopes),
            'response_type': 'code'
        }
        
        return f"https://www.facebook.com/dialog/oauth?{urlencode(params)}"
    
    def start_auth_server(self, port=8000):
        """Start a simple HTTP server to catch the redirect with the auth code"""
        self.server_port = port
        
        # Define handler to capture the authorization code
        class AuthCodeHandler(http.server.BaseHTTPRequestHandler):
            def do_GET(self):
                # Only handle the callback path
                if self.path.startswith('/callback'):
                    # Parse the URL to extract the code parameter
                    query = urllib.parse.urlparse(self.path).query
                    query_components = dict(urllib.parse.parse_qsl(query))
                    
                    # Extract the authorization code
                    if 'code' in query_components:
                        self.outer_instance.auth_code = query_components['code']
                        self.send_response(200)
                        self.send_header('Content-type', 'text/html')
                        self.end_headers()
                        self.wfile.write(b"<html><body><h1>Authentication successful!</h1><p>You can close this window now.</p></body></html>")
                    else:
                        self.send_response(400)
                        self.send_header('Content-type', 'text/html')
                        self.end_headers()
                        self.wfile.write(b"<html><body><h1>Authentication failed!</h1><p>No authorization code received.</p></body></html>")
                else:
                    self.send_response(404)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    self.wfile.write(b"<html><body><h1>Not Found</h1><p>This is not the callback URL.</p></body></html>")
        
        # Add a reference to the outer instance
        AuthCodeHandler.outer_instance = self
        
        # Create and start the server in a separate thread
        self.httpd = socketserver.TCPServer(("", port), AuthCodeHandler)
        self.server_thread = threading.Thread(target=self.httpd.serve_forever)
        self.server_thread.daemon = True
        self.server_thread.start()
        
        print(f"Server started at http://localhost:{port}")
        print("Waiting for authentication...")
    
    def stop_auth_server(self):
        """Stop the HTTP server"""
        if hasattr(self, 'httpd'):
            self.httpd.shutdown()
            self.httpd.server_close()
            print("Server stopped")
    
    def get_short_lived_token(self):
        """Exchange the authorization code for a short-lived access token"""
        if not self.auth_code:
            raise ValueError("No authorization code available. Run the authorization flow first.")
        
        url = "https://graph.facebook.com/v18.0/oauth/access_token"
        params = {
            'client_id': self.app_id,
            'client_secret': self.app_secret,
            'redirect_uri': self.redirect_uri,
            'code': self.auth_code
        }
        
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            self.access_token = data.get('access_token')
            return self.access_token
        else:
            print(f"Error getting access token: {response.text}")
            return None
    
    def exchange_for_long_lived_token(self):
        """Exchange a short-lived token for a long-lived one (valid for ~60 days)"""
        if not self.access_token:
            raise ValueError("No short-lived access token available.")
        
        url = "https://graph.facebook.com/v18.0/oauth/access_token"
        params = {
            'grant_type': 'fb_exchange_token',
            'client_id': self.app_id,
            'client_secret': self.app_secret,
            'fb_exchange_token': self.access_token
        }
        
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            self.long_lived_token = data.get('access_token')
            return self.long_lived_token
        else:
            print(f"Error getting long-lived token: {response.text}")
            return None
    
    def get_token_info(self, token=None):
        """Get information about an access token"""
        token_to_check = token or self.long_lived_token or self.access_token
        
        if not token_to_check:
            raise ValueError("No token available to check.")
        
        url = "https://graph.facebook.com/debug_token"
        params = {
            'input_token': token_to_check,
            'access_token': f"{self.app_id}|{self.app_secret}"
        }
        
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error checking token: {response.text}")
            return None
    
    def get_user_instagram_accounts(self):
        """Get the user's Instagram business accounts"""
        if not (self.long_lived_token or self.access_token):
            raise ValueError("No access token available.")
        
        token = self.long_lived_token or self.access_token
        
        # First, get the user's Facebook pages
        url = "https://graph.facebook.com/v18.0/me/accounts"
        params = {
            'access_token': token
        }
        
        response = requests.get(url, params=params)
        if response.status_code != 200:
            print(f"Error getting Facebook pages: {response.text}")
            return None
        
        pages = response.json().get('data', [])
        if not pages:
            print("No Facebook pages found.")
            return None
        
        # For each page, check if it has an Instagram business account
        instagram_accounts = []
        for page in pages:
            page_id = page.get('id')
            page_name = page.get('name')
            page_token = page.get('access_token')
            
            ig_url = f"https://graph.facebook.com/v18.0/{page_id}/"
            ig_params = {
                'fields': 'instagram_business_account',
                'access_token': page_token
            }
            
            ig_response = requests.get(ig_url, params=ig_params)
            if ig_response.status_code == 200:
                ig_data = ig_response.json()
                if 'instagram_business_account' in ig_data:
                    instagram_accounts.append({
                        'page_id': page_id,
                        'page_name': page_name,
                        'page_token': page_token,
                        'instagram_account_id': ig_data['instagram_business_account']['id']
                    })
        
        return instagram_accounts
    
    def run_auth_flow(self):
        """Run the full authorization flow"""
        try:
            # Start the server to catch the redirect
            self.start_auth_server()
            
            # Open the authorization URL in the browser
            auth_url = self.get_auth_url()
            print(f"Opening browser to: {auth_url}")
            webbrowser.open(auth_url)
            
            # Wait for the authorization code
            max_wait_time = 120  # 2 minutes
            wait_interval = 1  # 1 second
            total_waited = 0
            
            while not self.auth_code and total_waited < max_wait_time:
                time.sleep(wait_interval)
                total_waited += wait_interval
            
            if not self.auth_code:
                print("Timed out waiting for authorization code.")
                return False
            
            print(f"Received authorization code: {self.auth_code[:10]}...")
            
            # Exchange the code for a short-lived access token
            short_lived_token = self.get_short_lived_token()
            if not short_lived_token:
                return False
            
            print(f"Received short-lived access token: {short_lived_token[:10]}...")
            
            # Exchange for a long-lived access token
            long_lived_token = self.exchange_for_long_lived_token()
            if not long_lived_token:
                return False
            
            print(f"Received long-lived access token: {long_lived_token[:10]}...")
            
            # Get token information
            token_info = self.get_token_info(long_lived_token)
            if token_info and 'data' in token_info:
                expires_at = token_info['data'].get('expires_at')
                if expires_at:
                    expires_at_readable = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(expires_at))
                    print(f"Token expires at: {expires_at_readable}")
            
            # Get Instagram accounts
            instagram_accounts = self.get_user_instagram_accounts()
            if instagram_accounts:
                print("\nFound Instagram Business Accounts:")
                for i, account in enumerate(instagram_accounts, 1):
                    print(f"{i}. Page: {account['page_name']} (ID: {account['page_id']})")
                    print(f"   Instagram Account ID: {account['instagram_account_id']}")
                    print(f"   Page Token: {account['page_token'][:10]}...\n")
            else:
                print("No Instagram Business Accounts found.")
            
            return True
            
        finally:
            # Always stop the server
            self.stop_auth_server()


# Example usage
if __name__ == "__main__":
    # Replace these with your actual app details
    APP_ID = os.getenv("APP_ID")
    APP_SECRET = os.getenv("APP_SECRET")
    REDIRECT_URI = "http://localhost:8000/callback"
    
    auth = InstagramAuth(APP_ID, APP_SECRET, REDIRECT_URI)
    success = auth.run_auth_flow()
    
    if success:
        print("Authentication completed successfully!")
        print("\nStore these values securely for your application:")
        print(f"Long-lived Access Token: {auth.long_lived_token}")
        
        # If Instagram accounts were found, let user pick one
        instagram_accounts = auth.get_user_instagram_accounts()
        if instagram_accounts:
            account = instagram_accounts[0]  # Just use the first one for simplicity
            print(f"\nUsing Instagram Account ID: {account['instagram_account_id']}")
            print(f"With Page Token: {account['page_token']}")
    else:
        print("Authentication failed.")
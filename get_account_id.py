from test2 import InstagramAuth
import os
import dotenv
import json

dotenv.load_dotenv()

# Your long-lived access token
ACCESS_TOKEN = os.getenv("LONG_ACCESS_TOKEN")

# Initialize the auth class with dummy values since we already have the token
auth = InstagramAuth(
    app_id=os.getenv("APP_ID"),
    app_secret=os.getenv("APP_SECRET"),
    redirect_uri="http://localhost:8000/callback"
)

# Set the access token directly
auth.long_lived_token = ACCESS_TOKEN

# First, check if the token is valid
print("Checking token validity...")
token_info = auth.get_token_info()
if token_info:
    print("\nToken Information:")
    print(json.dumps(token_info, indent=2))
    
    # Check if we have the required permissions
    if 'data' in token_info and 'scopes' in token_info['data']:
        print("\nToken Scopes:")
        print(json.dumps(token_info['data']['scopes'], indent=2))
else:
    print("Token validation failed. The token might be invalid or expired.")

# Try to get Instagram accounts
print("\nAttempting to get Instagram accounts...")
accounts = auth.get_user_instagram_accounts()
if accounts:
    print("\nFound Instagram Business Accounts:")
    for i, account in enumerate(accounts, 1):
        print(f"{i}. Page: {account['page_name']} (ID: {account['page_id']})")
        print(f"   Instagram Account ID: {account['instagram_account_id']}")
        print(f"   Page Token: {account['page_token'][:10]}...\n")
else:
    print("No Instagram Business Accounts found.")

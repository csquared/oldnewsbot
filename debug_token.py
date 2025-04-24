import requests
import json

# Your long-lived access token
ACCESS_TOKEN = "EAADGeTNJ1wwBO2TTCkxavd0469ZBXyZAf8P3NXq3t1sxdI57C5ROoTpqxjwoXcO9ZCgNV9DicXM8QYJKAzTBYbz3m7j2NtxiZBs1aPvYpdHzCPha5U0FZAUqbEI9K8IWIgRwZCLs2NNvJhxHW20bhZAdejkUpiPjLlpYq97nEfO7JLIVPWJqdrZAO9QQtbm4dXtGMAZDZD"

# Your Facebook page ID from the granular scopes
PAGE_ID = "477006882171967"

# Debug the token
print("Debugging token...")
url = "https://graph.facebook.com/debug_token"
params = {
    'input_token': ACCESS_TOKEN,
    'access_token': ACCESS_TOKEN  # We can use the same token to debug itself
}

response = requests.get(url, params=params)
if response.status_code == 200:
    debug_data = response.json()
    print("\nToken Debug Information:")
    print(json.dumps(debug_data, indent=2))
    
    if 'data' in debug_data:
        data = debug_data['data']
        print("\nKey Information:")
        print(f"User ID: {data.get('user_id')}")
        print(f"App ID: {data.get('app_id')}")
        print(f"Type: {data.get('type')}")
        print(f"Application: {data.get('application')}")
        print(f"Data Access Expires At: {data.get('data_access_expires_at')}")
        print(f"Expires At: {data.get('expires_at')}")
        print(f"Is Valid: {data.get('is_valid')}")
        print(f"Issued At: {data.get('issued_at')}")
        print(f"Scopes: {', '.join(data.get('scopes', []))}")
else:
    print(f"Error debugging token: {response.text}")

# Try to get user info
print("\nGetting user information...")
url = "https://graph.facebook.com/me"
params = {
    'fields': 'id,name,accounts{id,name,access_token,instagram_business_account{id}}',
    'access_token': ACCESS_TOKEN
}

response = requests.get(url, params=params)
if response.status_code == 200:
    user_data = response.json()
    print("\nUser Information:")
    print(json.dumps(user_data, indent=2))
else:
    print(f"Error getting user info: {response.text}")

# Get Instagram business account through the page
print(f"\nGetting Instagram business account for page {PAGE_ID}...")
url = f"https://graph.facebook.com/v18.0/{PAGE_ID}"
params = {
    'fields': 'instagram_business_account{id,username}',
    'access_token': ACCESS_TOKEN
}

response = requests.get(url, params=params)
if response.status_code == 200:
    page_data = response.json()
    print("\nPage Information:")
    print(json.dumps(page_data, indent=2))
    
    if 'instagram_business_account' in page_data:
        ig_account = page_data['instagram_business_account']
        print("\nInstagram Business Account Found!")
        print(f"ID: {ig_account['id']}")
        print(f"Username: {ig_account.get('username', 'Not available')}")
    else:
        print("\nNo Instagram business account found for this page.")
        print("Make sure:")
        print("1. The Facebook page is published (not in draft mode)")
        print("2. The page is connected to an Instagram business account")
        print("3. You have admin access to the page")
else:
    print(f"Error getting page info: {response.text}") 
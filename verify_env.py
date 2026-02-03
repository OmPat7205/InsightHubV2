import os
from dotenv import load_dotenv, find_dotenv

def verify():
    print("--- Verifying Environment Configuration ---")
    
    # Check for .env file
    env_path = find_dotenv()
    if env_path:
        print(f"✅ Found .env file at: {env_path}")
    else:
        print("❌ Could NOT find .env file.")
        print("   -> Please create a file named .env in the root project folder.")
        return

    # Load environment
    load_dotenv(env_path)
    
    # Check for API Key
    api_key = os.getenv("GROQ_API_KEY")
    if api_key and api_key != "your_key_here":
        # Mask key for security
        masked_key = api_key[:4] + "*" * (len(api_key) - 8) + api_key[-4:]
        print(f"✅ Found GROQ_API_KEY: {masked_key}")
        print("   -> Environment is correctly configured!")
    elif api_key == "your_key_here":
        print("⚠️  Found GROQ_API_KEY but it is still the placeholder default.")
        print("   -> Please open .env and paste your actual API Key.")
    else:
        print("❌ GROQ_API_KEY not found in environment.")
        print("   -> Please check your .env file syntax.")

if __name__ == "__main__":
    verify()

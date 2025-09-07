import requests
import os
import hashlib
from urllib.parse import urlparse
from pathlib import Path

def main():
    print("Welcome to the Ubuntu Image Fetcher")
    print("A tool for mindfully collecting images from the web\n")
    print("Ubuntu Principle: 'I am because we are' - connecting communities through shared resources\n")
    
    # Get URLs from user
    urls_input = input("Please enter one or more image URLs (separated by commas): ")
    urls = [url.strip() for url in urls_input.split(',') if url.strip()]
    
    if not urls:
        print("No URLs provided. Exiting.")
        return
    
    # Create directory if it doesn't exist
    os.makedirs("Fetched_Images", exist_ok=True)
    
    successful_downloads = 0
    
    for url in urls:
        try:
            print(f"\nAttempting to fetch: {url}")
            
            # First, make a HEAD request to check headers before downloading
            head_response = requests.head(url, timeout=10, allow_redirects=True)
            head_response.raise_for_status()
            
            # Check important HTTP headers
            content_type = head_response.headers.get('Content-Type', '')
            content_length = head_response.headers.get('Content-Length')
            
            if not content_type.startswith('image/'):
                print(f"⚠️  Warning: URL doesn't appear to be an image (Content-Type: {content_type})")
                proceed = input("Do you want to continue anyway? (y/N): ").lower().strip()
                if proceed != 'y':
                    print("Skipping this URL.")
                    continue
            
            if content_length and int(content_length) > 10 * 1024 * 1024:  # 10MB limit
                print(f"⚠️  Warning: Image is large ({int(content_length) / 1024 / 1024:.2f} MB)")
                proceed = input("Do you want to continue? (y/N): ").lower().strip()
                if proceed != 'y':
                    print("Skipping this URL.")
                    continue
            
            # Now make the GET request to fetch the image
            response = requests.get(url, timeout=30, stream=True)
            response.raise_for_status()
            
            # Extract filename from URL or generate one
            parsed_url = urlparse(url)
            filename = os.path.basename(parsed_url.path)
            
            if not filename or '.' not in filename:
                # Try to get extension from content type
                ext = content_type.split('/')[-1] if '/' in content_type else 'jpg'
                filename = f"downloaded_image.{ext}"
            
            filepath = os.path.join("Fetched_Images", filename)
            
            # Check for duplicate by content
            content_hash = hashlib.md5(response.content).hexdigest()
            if is_duplicate_image(content_hash):
                print(f"⏭️  Skipping duplicate image: {filename}")
                continue
            
            # Save the image
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            # Save the hash to prevent future duplicates
            save_image_hash(content_hash, filename)
            
            print(f"✓ Successfully fetched: {filename}")
            print(f"✓ Image saved to {filepath}")
            successful_downloads += 1
            
        except requests.exceptions.RequestException as e:
            print(f"✗ Connection error: {e}")
        except Exception as e:
            print(f"✗ An error occurred: {e}")
    
    print(f"\nDownloaded {successful_downloads} of {len(urls)} images")
    print("\nConnection strengthened. Community enriched.")

def is_duplicate_image(content_hash):
    """Check if an image with this hash has already been downloaded"""
    hash_file = Path("Fetched_Images/downloaded_hashes.txt")
    if not hash_file.exists():
        return False
    
    with open(hash_file, 'r') as f:
        existing_hashes = [line.split('|')[0].strip() for line in f.readlines()]
    
    return content_hash in existing_hashes

def save_image_hash(content_hash, filename):
    """Save the image hash to prevent future duplicates"""
    hash_file = Path("Fetched_Images/downloaded_hashes.txt")
    with open(hash_file, 'a') as f:
        f.write(f"{content_hash}|{filename}\n")

if __name__ == "__main__":
    main()
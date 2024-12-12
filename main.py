from playwright.sync_api import sync_playwright
import argparse
import json
import csv
import random
import time
import sys
import os
from pathlib import Path
import pickle

def parse_args():
    parser = argparse.ArgumentParser(description='Scrape LinkedIn posts from a profile')
    parser.add_argument('--handle', help='LinkedIn profile handle (e.g., johndoe from linkedin.com/in/johndoe)')
    parser.add_argument('--scrolls', type=int, default=50, help='Number of times to scroll the page (default: 50)')
    parser.add_argument('--output-dir', type=str, default='output', help='Directory to save output files')
    return parser.parse_args()

def random_sleep():
    """Sleep for 1 second ± 500ms"""
    time.sleep(1 + random.uniform(-0.5, 0.5))

def load_browser_context():
    """Attempt to load saved browser context for LinkedIn"""
    storage_state_path = Path('linkedin_session.pkl')
    if not storage_state_path.exists():
        print("Error: No saved LinkedIn session found. Please run li_login.py first.")
        sys.exit(1)
    return storage_state_path

def extract_posts(page):
    """Extract post data using JavaScript"""
    return page.evaluate("""
        () => {
            const posts = [];
            const postElements = document.querySelectorAll('.fie-impression-container');
            
            postElements.forEach(post => {
                try {
                    const postData = {
                        posterName: post.querySelector('.update-components-actor__title span')?.innerText?.trim(),
                        posterProfile: post.querySelector('.update-components-actor__meta-link')?.href,
                        postDate: post.querySelector('.update-components-actor__sub-description')?.innerText?.trim(),
                        postText: post.querySelector('.update-components-text span.break-words')?.innerText?.trim(),
                        reactionsCount: post.querySelector('.social-details-social-counts__reactions-count')?.innerText?.trim(),
                        commentsCount: post.querySelector('.social-details-social-counts__comments span')?.innerText?.trim(),
                        repostCount: post.querySelector('.social-details-social-counts__item:nth-child(2) button span')?.innerText?.trim()
                    };
                    posts.push(postData);
                } catch (e) {
                    console.error('Error extracting post:', e);
                }
            });
            return posts;
        }
    """)

def save_output(posts, output_dir, handle):
    """Save posts to both JSON and CSV formats"""
    os.makedirs(output_dir, exist_ok=True)
    base_filename = f"{handle}_posts"
    
    # Save JSON
    json_path = os.path.join(output_dir, f"{base_filename}.json")
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(posts, f, indent=2, ensure_ascii=False)
    
    # Save CSV
    csv_path = os.path.join(output_dir, f"{base_filename}.csv")
    if posts:
        with open(csv_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=posts[0].keys())
            writer.writeheader()
            writer.writerows(posts)
    
    print(f"Saved {len(posts)} posts to:")
    print(f"- {json_path}")
    print(f"- {csv_path}")

def main():
    args = parse_args()
    
    if not args.handle:
        print("Error: LinkedIn profile handle is required")
        sys.exit(1)
    
    storage_state_path = load_browser_context()
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        with open(storage_state_path, 'rb') as f:
            context = browser.new_context(storage_state=pickle.load(f))
        page = context.new_page()
        
        # Navigate to profile's activity page
        activity_url = f"https://linkedin.com/in/{args.handle}/recent-activity/all/"
        print(f"Navigating to {activity_url}")
        page.goto(activity_url)
        
        # Scroll the page
        print(f"Scrolling page {args.scrolls} times...")
        for i in range(args.scrolls):
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            random_sleep()
            if (i + 1) % 10 == 0:
                print(f"Completed {i + 1} scrolls")
        
        # Extract posts
        print("Extracting posts...")
        posts = extract_posts(page)
        
        # Save output
        save_output(posts, args.output_dir, args.handle)
        
        browser.close()

if __name__ == "__main__":
    main()

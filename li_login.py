from playwright.sync_api import sync_playwright
import pickle
import os

def save_session(context):
    storage_state = context.storage_state()
    with open('linkedin_session.pkl', 'wb') as f:
        pickle.dump(storage_state, f)
    print("Session saved!")

def main():
    with sync_playwright() as p:
        # Launch browser in non-headless mode so user can interact
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        
        # Navigate to LinkedIn
        page.goto('https://www.linkedin.com')
        
        print("Please log in manually. Close the browser window when finished to save the session.")
        
        # Wait for browser to close
        try:
            page.wait_for_event('close', timeout=300000)  # 5 minute timeout
            save_session(context)
        except:
            print("Timeout or error occurred")
        finally:
            browser.close()

if __name__ == "__main__":
    main()

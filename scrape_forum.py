import os
import requests
import json
from dotenv import load_dotenv

DISCOURSE_URL = "https://discourse.onlinedegree.iitm.ac.in"
SEARCH_URL = f"{DISCOURSE_URL}/search.json?q=%23courses:tds-kb after:2024-12-31 before:2025-04-15"

load_dotenv()

def create_authenticated_session():
    session = requests.Session()
    session.cookies.set('_t', os.getenv("DISCOURSE_T_COOKIE"), domain="discourse.onlinedegree.iitm.ac.in")
    session.cookies.set('_forum_session', os.getenv("DISCOURSE_SESSION_COOKIE"), domain="discourse.onlinedegree.iitm.ac.in")
    return session

def extract_post_text(post):
    user = post["username"]
    cooked = post["cooked"]
    return f"{user}: {cooked.strip().replace('<p>', '').replace('</p>', '')}"

def fetch_thread(session, topic_id, slug):
    thread_url = f"{DISCOURSE_URL}/t/{slug}/{topic_id}.json"
    r = session.get(thread_url)
    r.raise_for_status()
    return r.json()

def main():
    session = create_authenticated_session()

    # Test auth
    test = session.get(f"{DISCOURSE_URL}/session/current.json")
    if test.status_code != 200:
        print("❌ Cookie auth failed. Please re-check your .env.")
        return
    print("✅ Authenticated as:", test.json()["current_user"]["username"])

    # Get search results (filtered)
    r = session.get(SEARCH_URL)
    r.raise_for_status()
    topics = r.json().get("topics", [])

    print(f"🔍 Found {len(topics)} topics to process.")

    all_text = []

    for topic in topics[:10]:  # Limit to first 10 for now
        try:
            topic_id = topic["id"]
            slug = topic["slug"]
            title = topic["title"]

            thread = fetch_thread(session, topic_id, slug)
            posts = thread["post_stream"]["posts"]

            thread_text = [f"\n--- {title} ---\n"]
            for post in posts:
                thread_text.append(extract_post_text(post))

            all_text.append("\n".join(thread_text))

        except Exception as e:
            print(f"❌ Skipping topic {topic['id']}: {e}")

    with open("forum_context.txt", "w", encoding="utf-8") as f:
        f.write("\n\n".join(all_text))

    print("✅ Saved scraped content to forum_context.txt")

if __name__ == "__main__":
    main()


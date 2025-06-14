import requests
from bs4 import BeautifulSoup
import json
import time

def get_post_content(url):
    """Fetch title and post content from a single Discourse topic URL."""
    try:
        print(f"📝 Scraping: {url}")
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        title = soup.find("title").text.strip()
        posts = soup.select(".cooked")  # .cooked contains the HTML-rendered post body
        content = "\n\n".join(post.get_text().strip() for post in posts)

        return {
            "title": title,
            "url": url,
            "content": content
        }

    except Exception as e:
        print(f"❌ Failed to scrape {url}: {e}")
        return None

def scrape_from_link_file(link_file="C:\\Users\\Admin\\Documents\\iitm tds project\\tdspro1\\tds_links.txt", output_file="C:\\Users\\Admin\\Documents\\iitm tds project\\tdspro1\\discourse_tds_posts.json"):
    """Reads links from a file, scrapes each one, and saves output to a JSON file."""
    with open(link_file, "r", encoding="utf-8") as f:
        # Handle numbered lines like '1. https://...'
        urls = [
            line.strip().split(". ", 1)[-1] if ". " in line else line.strip()
            for line in f
            if line.strip().startswith("http")
        ]

    print(f"🔗 Found {len(urls)} links to scrape.")
    all_posts = []

    for i, url in enumerate(urls, start=1):
        post = get_post_content(url)
        if post:
            all_posts.append(post)
        time.sleep(1)  # polite delay

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(all_posts, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Scraped {len(all_posts)} posts and saved to '{output_file}'")

if __name__ == "__main__":
    scrape_from_link_file()

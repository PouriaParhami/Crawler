import asyncio
import os
import json
import aiofiles
import database_generator
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from pydantic import BaseModel, Field
from crawl4ai import AsyncWebCrawler
from crawl4ai.async_configs import BrowserConfig, CrawlerRunConfig, CacheMode
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator
from crawl4ai.content_filter_strategy import LLMContentFilter, PruningContentFilter, BM25ContentFilter
from crawl4ai.extraction_strategy import LLMExtractionStrategy
from dotenv import load_dotenv
from base64 import b64decode
from datetime import datetime

load_dotenv()
database_generator.create_news_links_table()

RESOURCE_FOLDER = os.path.join(os.path.dirname(__file__), 'resource')
CONTENT_FOLDER = os.path.join(RESOURCE_FOLDER, 'content')
HTML_FOLDER = os.path.join(RESOURCE_FOLDER, 'html')
IMAGES_FOLDER = os.path.join(RESOURCE_FOLDER, 'images')
JSON_FOLDER = os.path.join(RESOURCE_FOLDER, 'json')
MARKDOWN_FOLDER = os.path.join(RESOURCE_FOLDER, 'markdown')
PDFS_FOLDER = os.path.join(RESOURCE_FOLDER, 'pdfs')
VIDEOS_FOLDER = os.path.join(RESOURCE_FOLDER, 'videos')

news_urls = [
    "https://www.irna.ir/",
    "https://www.isna.ir/",
    "https://www.farsnews.ir/",
    "https://kayhan.ir/",
    "https://www.tasnimnews.com/",
    "https://www.iribnews.ir/",
    "https://www.yjc.ir/",
    "https://www.hamshahrionline.ir/",
    "https://www.khabaronline.ir/",
    "https://www.varzesh3.com/",
    "https://donya-e-eqtesad.com/",
    "https://www.eghtesadonline.com/"
]

async def save_text(text_content, prefix, postfix):
    text_file = os.path.join(CONTENT_FOLDER, f"{prefix}_full_text_{postfix}.txt")
    async with aiofiles.open(text_file, 'w', encoding='utf-8') as f:
        await f.write(text_content)
    print(f"Saved text to {text_file}")

async def save_screenshot(screenshot_data, prefix, postfix):
    image_file = os.path.join(IMAGES_FOLDER, f"{prefix}_screenshot_{postfix}.png")
    async with aiofiles.open(image_file, 'wb') as f:
        await f.write(b64decode(screenshot_data))
    print(f"Saved screenshot to {image_file}")
    
# تابع نرمال‌سازی URL
def normalize_url(url):
    parsed_url = urlparse(url)
    # فقط مسیر اصلی و دامنه رو نگه می‌داریم، پارامترهای اضافی رو حذف می‌کنیم
    clean_url = urlunparse((parsed_url.scheme, parsed_url.netloc, parsed_url.path, '', '', ''))
    return clean_url


async def main():
    """
    Main function to run the web crawler asynchronously.
    This function sets up the browser and crawler configurations, runs the crawler on a list of news URLs,
    and processes the results. It saves the filtered news links to a JSON file, inserts them into a SQLite
    database, and saves screenshots and PDFs of the crawled pages.
    Configurations:
    - BrowserConfig: Configuration for the browser, including verbosity and headless mode.
    - CrawlerRunConfig: Configuration for the crawler, including content filtering, cache mode, and output options.
    Workflow:
    1. Initialize browser and crawler configurations.
    2. Run the crawler on the provided list of news URLs.
    3. For each successful result:
        - Filter internal links to include only those with "news" in their path.
        - Save the filtered links and their titles to a JSON file.
        - Insert the filtered links into a SQLite database.
        - Save a PDF of the crawled page if available.
        - Save a screenshot of the crawled page if available.
    4. Print error messages for any failed crawls, PDFs, or screenshots.
    Returns:
        None
    """
    
    browser_config = BrowserConfig(
        verbose=True,
        headless=True,
        )  # Default browser configuration
    
    crawler_config = CrawlerRunConfig(
        # Content filtering
        word_count_threshold=5,
        exclude_external_images=True,
        exclude_external_links=True,
        remove_overlay_elements=True,
        process_iframes=True,
        excluded_tags=['footer', 'header', 'nav'],
        
        # agent act like user
        magic=True,
        
        # Cache mode
        cache_mode=CacheMode.BYPASS, 
        
        # Screenshot and pdf
        screenshot=True,
        pdf=True,
        
    )   # Default crawl run configuration

    async with AsyncWebCrawler(config=browser_config) as crawler:
        results = await crawler.arun_many(
            urls=news_urls,
            config=crawler_config
        )
        for result in results:
            if result.success:
                now = datetime.now()
                postfix_file_name = now.strftime("%Y-%m-%d_%H-%M-%S")
                prefix_file_name = result.links["internal"][0]["base_domain"]
                
                unique_links = set()
                clean_internal_links = []

                # Clean unrelated news links (just check news in the path of url not base domain)
                for link in result.links['internal']:
                    parsed_url = urlparse(link["href"])
                    if "news" in parsed_url.path:
                        normalized_url = normalize_url(link["href"])
                        if normalized_url not in unique_links:
                            unique_links.add(normalized_url)
                            clean_internal_links.append(link)
                    
                # Save news links and titles into json file
                json_data = json.dumps(clean_internal_links, ensure_ascii=False, indent=4)
                with open(os.path.join(JSON_FOLDER, f"{prefix_file_name}_raw_news_links_{postfix_file_name}.json"), 'w', encoding="utf-8") as f:
                    f.write(json_data)
                
                # Inser into sqlit3 database
                for link in clean_internal_links:
                    database_generator.insert_news_link(link["text"], link["href"], link["base_domain"], postfix_file_name, "I need to thing about it.")
                    # print(f"title: {link['text']}, link: {link['href']}\n")
                
                # Save pdf
                if result.pdf:
                    # pdf_bytes = b64decode(result.pdf)
                    with open(os.path.join(PDFS_FOLDER, f"{prefix_file_name}_homepage_{postfix_file_name}.pdf"), "wb") as f:
                        f.write(result.pdf)
                else:
                    print(f"PDF failed: {result.error_message}")
                    print(f"PDF Status code: {result.status_code}")

                # Save Screen Shot
                if result.screenshot:
                    with open(os.path.join(IMAGES_FOLDER, f"{prefix_file_name}_homepage_{postfix_file_name}.png"), "wb") as f:
                        f.write(b64decode(result.screenshot))
                else:
                    print(f"Screen Shot failed: {result.error_message}")
                    print(f"Screen Shot Status code: {result.status_code}")

            else:
                print(f"Crawl failed: {result.error_message}")
                print(f"Status code: {result.status_code}")

if __name__ == "__main__":
    asyncio.run(main())




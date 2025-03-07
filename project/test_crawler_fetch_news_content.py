import asyncio
import os
import json
import news_paper_utils
import time
import aiofiles
import re
import database_generator
from urllib.parse import urlparse, urlsplit
from pydantic import BaseModel, Field
from crawl4ai import AsyncWebCrawler
from crawl4ai.async_configs import BrowserConfig, CrawlerRunConfig, CacheMode
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator
from crawl4ai.content_filter_strategy import LLMContentFilter, PruningContentFilter, BM25ContentFilter
from crawl4ai.extraction_strategy import LLMExtractionStrategy
from dotenv import load_dotenv
from base64 import b64decode
from datetime import datetime
from bs4 import BeautifulSoup

load_dotenv()

RESOURCE_FOLDER = os.path.join(os.path.dirname(__file__), 'resource')
CONTENT_FOLDER = os.path.join(RESOURCE_FOLDER, 'content')
HTML_FOLDER = os.path.join(RESOURCE_FOLDER, 'html')
IMAGES_FOLDER = os.path.join(RESOURCE_FOLDER, 'images')
JSON_FOLDER = os.path.join(RESOURCE_FOLDER, 'json')
MARKDOWN_FOLDER = os.path.join(RESOURCE_FOLDER, 'markdown')
PDFS_FOLDER = os.path.join(RESOURCE_FOLDER, 'pdfs')
VIDEOS_FOLDER = os.path.join(RESOURCE_FOLDER, 'videos')

for folder in [RESOURCE_FOLDER, CONTENT_FOLDER, IMAGES_FOLDER]:
    os.makedirs(folder, exist_ok=True)
    
def remove_links_from_markdown(markdown_content):
    # الگوی لینک در Markdown: [متن](آدرس)
    pattern = r'\[([^\]]+)\]\([^\)]+\)'
    # جایگزینی هر لینک با متن داخل کروشه‌ها
    cleaned_content = re.sub(pattern, r'\1', markdown_content)
    # حذف هر آدرس خالی که ممکنه باقی مونده باشه (مثل (http://...))
    cleaned_content = re.sub(r'\(http[s]?://[^\)]+\)', '', cleaned_content)
    return cleaned_content

def fetch_news_links_from_db():
    news_links = database_generator.select_news_link_from_news_links()
    url_links = [link[0] for link in news_links]
    return url_links

news_urls = fetch_news_links_from_db()[:10]
for news_url in news_urls:
    print(f"URLS are: {news_url}")

async def save_text(text_content, name, prefix, postfix):
    text_file = os.path.join(CONTENT_FOLDER, f"{prefix}_{name}_{postfix}.txt")
    async with aiofiles.open(text_file, 'w', encoding='utf-8') as f:
        await f.write(text_content)
    print(f"Saved text to {text_file}")

async def save_screenshot(screenshot_data, name, prefix, postfix):
    image_file = os.path.join(IMAGES_FOLDER, f"{prefix}_{name}_{postfix}.png")
    async with aiofiles.open(image_file, 'wb') as f:
        await f.write(b64decode(screenshot_data))
    print(f"Saved screenshot to {image_file}")

async def main():
    
    total_start_time = time.time()
    
    browser_config = BrowserConfig(
        verbose=True,
        headless=True,
        
        
        )  # Default browser configuration

    crawler_config = CrawlerRunConfig(
        word_count_threshold=1,  # حداقل کلمات کم باشه که چیزی از قلم نیفته
        magic=True,
        cache_mode=CacheMode.BYPASS,
        screenshot=True,  # اسکرین‌شات رو فعال می‌کنیم
        wait_for_images=True,
        page_timeout=60000,
        scan_full_page=True,
        only_text=True,
        wait_until="networkidle",  # صبر تا پایان درخواست‌های شبکه
        js_code="""() => {
            return new Promise((resolve) => {
                if (document.readyState === 'complete') {
                    resolve();
                } else {
                    window.addEventListener('load', () => {
                        setTimeout(resolve, 3000); // 3 ثانیه صبر اضافی
                    });
                }
            });
        }""",  # کد جاوااسکریپت برای اطمینان از بارگذاری کامل  # 5 ثانیه برای رندر جاوااسکریپت
        # screenshot_wait_for=2.0
        )

    async with AsyncWebCrawler(config=browser_config) as crawler:
        results = await crawler.arun_many(
            urls=news_urls,
            config=crawler_config
        )

        for result in results:
            
            url_start_time = time.time()
            now = datetime.now()
            postfix = now.strftime("%Y-%m-%d_%H-%M-%S")
            prefix = urlparse(result.url).netloc
            
            if result.success:
                
                cleaned_text = remove_links_from_markdown(result.markdown)
                
                path = urlsplit(result.url).path  # مسیر URL رو می‌گیره مثلاً /fa/news/4468084/
                parts = path.split('/')
                with open(os.path.join(MARKDOWN_FOLDER, f"{prefix}_news_content_{parts[-1]}_{postfix}.md"), "w",  encoding="utf-8") as f:
                    f.write(cleaned_text)
                
                # ذخیره اسکرین‌شات
                if result.screenshot:
                    await save_screenshot(result.screenshot, f"news_content_{parts[-1]}", prefix, postfix)
                else:
                    print(f"Screenshot failed for {result.url}: {result.error_message}")
            else:
                print(f"Crawl failed for {result.url}: {result.error_message}")
            
            url_duration = time.time() - url_start_time
            print(f"Processing {result.url} took {url_duration:.2f} seconds")
            
        total_duration = time.time() - total_start_time
        print(f"\nTotal execution time: {total_duration:.2f} seconds")
        print(f"Average time per URL: {total_duration / len(news_urls):.2f} seconds")
        
if __name__ == "__main__":
    asyncio.run(main())
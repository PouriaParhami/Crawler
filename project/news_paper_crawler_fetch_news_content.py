import asyncio
import os
import json
import news_paper_utils
import database_generator
from urllib.parse import urlparse
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

RESOURCE_FOLDER = os.path.join(os.path.dirname(__file__), 'res')
CONTENT_FOLDER = os.path.join(RESOURCE_FOLDER, 'content')
HTML_FOLDER = os.path.join(RESOURCE_FOLDER, 'html')
IMAGES_FOLDER = os.path.join(RESOURCE_FOLDER, 'images')
JSON_FOLDER = os.path.join(RESOURCE_FOLDER, 'json')
MARKDOWN_FOLDER = os.path.join(RESOURCE_FOLDER, 'markdown')
PDFS_FOLDER = os.path.join(RESOURCE_FOLDER, 'pdfs')
VIDEOS_FOLDER = os.path.join(RESOURCE_FOLDER, 'videos')



def fetch_news_links_from_db():
    news_links = database_generator.select_news_link_from_news_links()
    url_links = [link[0] for link in news_links]
    return url_links

news_urls = fetch_news_links_from_db()
news_urls_test = news_urls[:5]



class NewsContentExtraction(BaseModel):
    news_title: str
    news_content: str
    news_content_summary: str
    news_content_english_translate: str
    news_content_arabic_translate: str
    news_content_hebrew_translate: str
    news_content_summary_english_translate: str
    news_content_summary_arabic_translate: str
    news_content_summary_hebrew_translate: str


async def main():
    
    browser_config = BrowserConfig(
        verbose=True,
        headless=True,
        )  # Default browser configuration
    
    llm_extraction_strategy = LLMExtractionStrategy(
        provider=os.getenv("PROVIDER_NAME"),
        api_token=os.getenv("API_KEY"),
        schema=NewsContentExtraction.model_json_schema(),
        extraction_type="schema",
        instruction=news_paper_utils.LLM_EXTRACTION_STRATEGY_INSTRUCTION,
        output_format="json",
    )

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
        
        # Extraction Strategy
        extraction_strategy=llm_extraction_strategy,

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
            
            
            if result.success and result.extracted_content:
                
                # Create prefix and postfix for PDF, IMAGE, and JSON files name.
                now = datetime.now()
                postfix_file_name = now.strftime("%Y-%m-%d_%H-%M-%S")
                prefix_file_name = result.links["internal"][0]["base_domain"]

                processed_data = []
                
                # خروجی LLM به‌صورت JSON میاد
                news_data = json.loads(result.extracted_content)
                url = result.url
                postfix = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                prefix = urlparse(url).netloc

                # اضافه کردن URL به داده برای ردیابی
                news_data["url"] = url
                processed_data.append(news_data)


                # ذخیره همه داده‌ها توی یه فایل JSON
                if processed_data:
                    output_file = os.path.join(JSON_FOLDER, f"{prefix}_processed_news_{postfix}.json")
                    with open(output_file, 'w', encoding='utf-8') as f:
                        json.dump(processed_data, f, ensure_ascii=False, indent=4)
                    print(f"Saved processed news to {output_file}")


                # Save pdf
                if result.pdf:
                    # pdf_bytes = b64decode(result.pdf)
                    with open(os.path.join(PDFS_FOLDER, f"{prefix_file_name}_{news_paper_utils.PDF_CONTENT_NEWS_NAME}_{postfix_file_name}.pdf"), "wb") as f:
                        f.write(result.pdf)
                else:
                    print(f"PDF failed: {result.error_message}")
                    print(f"PDF Status code: {result.status_code}")

                # Save Screen Shot
                if result.screenshot:
                    with open(os.path.join(IMAGES_FOLDER, f"{prefix_file_name}_{news_paper_utils.IMAGE_CONTENT_NEWS_NAME}_{postfix_file_name}.png"), "wb") as f:
                        f.write(b64decode(result.screenshot))
                else:
                    print(f"Screen Shot failed: {result.error_message}")
                    print(f"Screen Shot Status code: {result.status_code}")

            else:
                print(f"Crawl failed: {result.error_message}")
                print(f"Status code: {result.status_code}")

if __name__ == "__main__":
    asyncio.run(main())
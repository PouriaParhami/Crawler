LLM_EXTRACTION_STRATEGY_INSTRUCTION = """
        From the webpage, perform the following tasks:
            1. Extract the main news article content (exclude ads, navigation, and footer).
            2. Extract the title of the news article.
            3. Summarize the main content into 2-3 sentences in Persian.
            4. Translate the main content into English.
            5. Translate the main content into Arabic
            6. Translate the main content into Hebrew
            7. Translate the summarized content into English
            8. Translate the summarized content into Arabic
            9. Translate the summarized content into Hebrew
        Return the result as a JSON object with the following keys:
            - "news_title": the article title
            - "news_content": the full extracted content
            - "news_content_summary": the summary in Persian
            - "news_content_english_translate": the translated content in English
            - "news_content_arabic_translate": the translated content in Arabic
            - "news_content_hebrew_translate": the translated content in Hebrew
            - "news_content_summary_english_translate"
            - "news_content_summary_arabic_translate"
            - "news_content_summary_hebrew_translate"

        """

LLM_CONTENT_FINTER_STRATEGY_INSTRUCTION ="""
        Extract all visible text content from the webpage, including paragraphs, headings, lists, navigation, footer, and any other text elements.
        Do not exclude any text, regardless of its location or purpose.
        Return the complete text as a single raw string (no JSON formatting).
        """


PDF_CONTENT_NEWS_NAME="news_content"
IMAGE_CONTENT_NEWS_NAME="news_content"

PDF_HOME_PAGE_NAME="home_page"
IMAGE_HOME_PAGE_NAME="home_page"
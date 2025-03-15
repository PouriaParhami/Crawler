import WebCrawler

# Website URLs
links = []

# Output resource files
results = []

for link in links:
    cralwer = WebCrawler.WebCrawler()
    paths = cralwer.get_screenshot_and_crawl_text(link)
    cralwer.close()
    results.append({
        'screenshot': paths[0],
        'text': paths[1]
    })

for result in results:
    # Store in database or do something else
    print(result)

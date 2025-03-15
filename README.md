# WebCrawler

A Python-based web crawling tool that captures screenshots of web pages and extracts their textual content while removing images and visual elements.

## Features

- Takes screenshots of web pages in headless mode
- Removes images, background images, and other visual elements before capturing
- Extracts textual content from web pages
- Automatically resizes browser to full page height for complete captures
- Saves both screenshots and text content with consistent naming

## Installation

### Prerequisites

- Python 3.6+
- Chrome browser
- ChromeDriver (compatible with your Chrome version)

### Dependencies

```
selenium
webdriver-manager
```

Install dependencies with pip:

```bash
pip install selenium webdriver-manager
```

## Usage

### Basic Usage

```python
import WebCrawler

# Initialize the crawler
crawler = WebCrawler.WebCrawler()

# Process a single URL
screenshot_path, text_path = crawler.get_screenshot_and_crawl_text("https://example.com")

# Always close the crawler when done
crawler.close()
```

### Processing Multiple URLs

```python
import WebCrawler

# Website URLs
links = ["https://example.com", "https://another-site.com"]

# Output resource files
results = []

for link in links:
    crawler = WebCrawler.WebCrawler()
    paths = crawler.get_screenshot_and_crawl_text(link)
    crawler.close()
    results.append({
        'screenshot': paths[0],
        'text': paths[1]
    })

for result in results:
    # Store in database or do something else
    print(result)
```

## API Reference

### Class: `WebCrawler`

#### Constructor

```python
WebCrawler(driver_path=None, output_folder="crawled")
```

- `driver_path`: Path to the ChromeDriver executable (optional). If not provided, Selenium will attempt to find it automatically.
- `output_folder`: Name of the folder where screenshots and text files will be saved (default: "crawled"). This folder will be created under the `resource` directory relative to the script.

#### Methods

##### `take_screenshot(url)`

Takes a screenshot of the specified URL after removing images and visual elements.

- **Parameters**:
  - `url`: The web page URL to screenshot
- **Returns**: Path to the saved screenshot file

##### `copy_and_save_text()`

Extracts text content from the current page and saves it to a text file.

- **Returns**: Path to the saved text file

##### `get_screenshot_and_crawl_text(url)`

Combines both screenshot capture and text extraction in one method.

- **Parameters**:
  - `url`: The web page URL to process
- **Returns**: A tuple containing `(screenshot_path, text_file_path)`

##### `close()`

Closes the browser and releases resources. Always call this method when you're done using the crawler.

##### `_hide_images()` (private)

Internal method that removes images from the page before taking a screenshot.

##### `_sanitize_filename(url)` (private)

Internal method that creates a consistent filename based on the URL's MD5 hash.

## File Storage

All output files are stored in the `resource/{output_folder}` directory relative to the script location:

- Screenshots are saved as PNG files with filenames based on the MD5 hash of the URL
- Text content is saved as TXT files with the same base name as the corresponding screenshot

## Example Output

For a URL like `https://example.com`:

```
resource/crawled/
├── 1ab5e93df39456e8d2aa342145c0f978.png  # Screenshot
└── 1ab5e93df39456e8d2aa342145c0f978.txt  # Extracted text
```

## Notes

- The crawler runs Chrome in headless mode, which means no browser UI will be displayed
- Screenshots are taken at 1920x1080 resolution, then extended to the full height of the page
- The tool waits for the page to load completely before processing
- All image elements are removed before taking screenshots
- Text extraction is performed by selecting all content and capturing it via JavaScript

## License

[Add your license information here]
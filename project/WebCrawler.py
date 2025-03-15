from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import os
import hashlib

class WebCrawler:
    def __init__(self, driver_path=None, output_folder="crawled"):
        # Creating a folder to store screenshots and extracted texts
        resource = os.path.join(os.path.dirname(__file__), 'resource')
        self.output_folder = os.path.join(resource, output_folder)
        os.makedirs(self.output_folder, exist_ok=True)
        options = Options()
        options.add_argument("--headless") # Running in headless mode
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        self.driver = webdriver.Chrome(service=Service(driver_path) if driver_path else None, options=options)
    
    def _sanitize_filename(self, url):
        self.imageFileName = hashlib.md5(url.encode()).hexdigest() + ".png"
        return self.imageFileName
    
    def _hide_images(self):
        script = """
        // Remove all <img> tags
        document.querySelectorAll('img').forEach(img => img.remove());

        // Remove all <source> tags that refer to image formats (like videos)
        document.querySelectorAll('source').forEach(source => {
            let src = source.getAttribute('src') || '';
            if (src.match(/\\.(svg|png|gif|jpeg|webp|jpg)$/i)) {
                source.remove();
            }
        });

        // Remove all sections that use background images
        document.querySelectorAll('*').forEach(element => {
            let style = window.getComputedStyle(element);
            let backgroundImage = style.getPropertyValue('background-image');
            let background = style.getPropertyValue('background');
            let backgroundUrl = background.match(/url\\(([^)]+)\\)/i);
            if (backgroundUrl) {
                element.style.background = 'none';  // Remove background
            }
            if (backgroundImage && backgroundImage.match(/\\.(svg|png|gif|jpeg|webp|jpg)$/i)) {
                element.style.backgroundImage = 'none';  // Remove background image
            }
        });

        // Remove all <picture> tags that contain images
        document.querySelectorAll('picture').forEach(picture => picture.remove());
        """
        
        self.driver.execute_script(script)
    
    def take_screenshot(self, url):
        self.driver.get(url)
        time.sleep(2)  # Waiting for the page to fully load
        self._hide_images()
        time.sleep(1)  # A little delay for JavaScript execution
        
        # Setting the browser height equal to the page height
        height = self.driver.execute_script("return document.body.scrollHeight")
        self.driver.set_window_size(1920, height)
        
        screenshot_path = os.path.join(self.output_folder, self._sanitize_filename(url))
        self.screenshot_path = screenshot_path
        self.driver.save_screenshot(screenshot_path)

        screenshot_path = os.path.join(self.output_folder, self._sanitize_filename(url))
        self.driver.save_screenshot(screenshot_path)
        print(f"Screenshot saved: {screenshot_path}")

        return screenshot_path
    
    def copy_and_save_text(self):
        # Press Ctrl+A to select all text first
        self.driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.CONTROL + 'a')
        time.sleep(0.5)  # Small delay after selection
        
        # Press Ctrl+C to copy the selected text
        self.driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.CONTROL + 'c')
        time.sleep(0.5)  # Small delay after copying
        
        # Execute JavaScript to get the text content
        text_content = self.driver.execute_script("""
        return document.body.innerText;
        """)
        
        # Create the text file path with the same name as the screenshot but .txt extension
        text_filename = os.path.splitext(self.imageFileName)[0] + ".txt"
        text_file_path = os.path.join(self.output_folder, text_filename)
        
        # Write the text content to the file
        with open(text_file_path, 'w', encoding='utf-8') as f:
            f.write(text_content)
        
        print(f"Text content saved: {text_file_path}")
        return text_file_path

    def get_screenshot_and_crawl_text(self, url):
        screenshot_path = self.take_screenshot(url)
        text_file_path = self.copy_and_save_text()
        return screenshot_path, text_file_path

    def close(self):
        self.driver.quit()

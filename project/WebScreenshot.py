from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import os
import hashlib

class WebScreenshot:
    def __init__(self, driver_path=None, output_folder="screenshots"):
        resource = os.path.join(os.path.dirname(__file__), 'resource')
        self.output_folder = os.path.join(resource, output_folder)
        os.makedirs(self.output_folder, exist_ok=True)
        options = Options()
        options.add_argument("--headless")  # اجرای بدون رابط گرافیکی
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        self.driver = webdriver.Chrome(service=Service(driver_path) if driver_path else None, options=options)
    
    def _sanitize_filename(self, url):
        return hashlib.md5(url.encode()).hexdigest() + ".png"
    
    def _hide_images(self):
        script = """
        let images = document.querySelectorAll('img');
        images.forEach(img => {
            let rect = img.getBoundingClientRect();
            let overlay = document.createElement('div');
            overlay.style.position = 'absolute';
            overlay.style.left = rect.left + 'px';
            overlay.style.top = rect.top + 'px';
            overlay.style.width = rect.width + 'px';
            overlay.style.height = rect.height + 'px';
            overlay.style.backgroundColor = 'white';
            overlay.style.zIndex = '9999';
            overlay.style.pointerEvents = 'none';
            document.body.appendChild(overlay);
        });
        """
        self.driver.execute_script(script)
    
    def take_screenshot(self, url):
        self.driver.get(url)
        time.sleep(2)  # منتظر لود کامل صفحه می‌مانیم
        self._hide_images()
        time.sleep(1)  # کمی تأخیر برای اجرای JavaScript
        
        screenshot_path = os.path.join(self.output_folder, self._sanitize_filename(url))
        self.driver.save_screenshot(screenshot_path)
        print(f"Screenshot saved: {screenshot_path}")
        return screenshot_path
    
    def close(self):
        self.driver.quit()

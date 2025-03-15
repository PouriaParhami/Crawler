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
        self.imageFileName = hashlib.md5(url.encode()).hexdigest() + ".png"
        return self.imageFileName
    
    def _hide_images(self):
        script = """
        // حذف تمامی تگ‌های <img>
        document.querySelectorAll('img').forEach(img => img.remove());

        // حذف تمامی تگ‌های <source> که به فرمت تصویری اشاره دارند (مثل ویدیوها)
        document.querySelectorAll('source').forEach(source => {
            let src = source.getAttribute('src') || '';
            if (src.match(/\\.(svg|png|gif|jpeg|webp|jpg)$/i)) {
                source.remove();
            }
        });

        // حذف تمامی بخش‌هایی که از پس‌زمینه‌ی تصویری استفاده می‌کنند
        document.querySelectorAll('*').forEach(element => {
            let style = window.getComputedStyle(element);
            let backgroundImage = style.getPropertyValue('background-image');
            let background = style.getPropertyValue('background');
            let backgroundUrl = background.match(/url\\(([^)]+)\\)/i);
            if (backgroundUrl) {
                element.style.background = 'none';  // حذف پس‌زمینه
            }
            if (backgroundImage && backgroundImage.match(/\\.(svg|png|gif|jpeg|webp|jpg)$/i)) {
                element.style.backgroundImage = 'none';  // حذف تصویر پس‌زمینه
            }
        });

        // حذف تمامی تگ‌های <picture> که تصویر درون خود دارند
        document.querySelectorAll('picture').forEach(picture => picture.remove());
        """
        
        self.driver.execute_script(script)
    
    def take_screenshot(self, url):
        self.driver.get(url)
        time.sleep(2)  # منتظر لود کامل صفحه می‌مانیم
        self._hide_images()
        time.sleep(1)  # کمی تأخیر برای اجرای JavaScript
        
        # تنظیم ارتفاع مرورگر برابر با ارتفاع صفحه
        height = self.driver.execute_script("return document.body.scrollHeight")
        self.driver.set_window_size(1920, height)
        
        screenshot_path = os.path.join(self.output_folder, self._sanitize_filename(url))
        self.screenshot_path = screenshot_path
        self.driver.save_screenshot(screenshot_path)

        screenshot_path = os.path.join(self.output_folder, self._sanitize_filename(url))
        self.driver.save_screenshot(screenshot_path)
        print(f"Screenshot saved: {screenshot_path}")
        return screenshot_path
    
    def close(self):
        self.driver.quit()

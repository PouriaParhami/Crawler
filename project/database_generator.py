import sqlite3

def create_news_links_table():

    # Create a connection to the database
    # Connect to SQLite database (or create it if it doesn't exist)
    conn = sqlite3.connect('news_paper_information.db')

    # Create a cursor object
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS news_links (
        news_id INTEGER PRIMARY KEY AUTOINCREMENT,
        news_title TEXT,
        news_link TEXT,
        news_provider TEXT,
        news_crawl_date TEXT,
        news_home_page_pic_address TEXT
    )
    ''')

    # Commit the changes and close the connection
    conn.commit()
    conn.close()

def insert_news_link(news_title, news_link, news_provider, news_crawl_date, news_home_page_pic_address):
        conn = sqlite3.connect('news_paper_information.db')
        cursor = conn.cursor()
        cursor.execute('''
        INSERT INTO news_links (news_title, news_link, news_provider, news_crawl_date, news_home_page_pic_address)
        VALUES (?, ?, ?, ?, ?)
        ''', (news_title, news_link, news_provider, news_crawl_date, news_home_page_pic_address))
        conn.commit()
        conn.close()

def update_news_link(news_id, news_title, news_link, news_provider, news_crawl_date, news_home_page_pic_address):
        conn = sqlite3.connect('news_paper_information.db')
        cursor = conn.cursor()
        cursor.execute('''
        UPDATE news_links
        SET news_title = ?, news_link = ?, news_provider = ?, news_crawl_date = ?, news_home_page_pic_address = ?
        WHERE news_id = ?
        ''', (news_title, news_link, news_provider, news_crawl_date, news_home_page_pic_address, news_id))
        conn.commit()
        conn.close()

def delete_news_link(news_id):
        conn = sqlite3.connect('news_paper_information.db')
        cursor = conn.cursor()
        cursor.execute('''
        DELETE FROM news_links
        WHERE news_id = ?
        ''', (news_id,))
        conn.commit()
        conn.close()

def select_all_news_links():
        conn = sqlite3.connect('news_paper_information.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM news_links')
        rows = cursor.fetchall()
        conn.close()
        return rows

def select_news_link_from_news_links():
        conn = sqlite3.connect('news_paper_information.db')
        cursor = conn.cursor()
        cursor.execute('SELECT news_link FROM news_links')
        rows = cursor.fetchall()
        conn.close()
        return rows

def select_news_link_by_id(news_id):
        conn = sqlite3.connect('news_paper_information.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM news_links WHERE news_id = ?', (news_id,))
        row = cursor.fetchone()
        conn.close()
        return row




Based on the provided code snippets, it seems like you're working on a project that involves scraping product data from Amazon and storing it in a MongoDB database. Here's a suggested description for your GitHub project:

Amazon Scraper
This project is a Python-based web scraper designed specifically for extracting product information from Amazon. It utilizes Selenium and BeautifulSoup for web scraping and interacts with MongoDB for data storage.

Features
Dynamic Web Scraping: The scraper dynamically extracts product details including title, price, rating, and number of reviews from Amazon product pages.
MongoDB Integration: Utilizes MongoDB to store scraped data efficiently.
Email Notifications: Sends email notifications in case of a price drop for any tracked products.

Requirements
Python 3.x
Selenium
BeautifulSoup
pymongo
dotenv
Usage
Clone the repository to your local machine.
Install the required dependencies using pip install -r requirements.txt.
Set up your MongoDB database and configure the connection details in the .env file.
Execute the main script main.py to start scraping Amazon product URLs and populating the database.
Configuration
Ensure you have set up your environment variables in the .env file as follows:


MONGODB_DOMAIN="Your MongoDB Cluster Domain"
MONGODB_USERNAME="Your MongoDB Username"
MONGODB_PASSWORD="Your MongoDB Password"
MONGODB_DBNAME="Your MongoDB Database Name"
SENDER_EMAIL="Your Email Address for Sending Notifications"
EMAIL_PASSWORD="Your Email Password"
Note
This scraper is designed for educational and personal use only. Ensure compliance with Amazon's terms of service and usage policies.
Use responsibly and avoid aggressive scraping to prevent IP bans or other restrictions.

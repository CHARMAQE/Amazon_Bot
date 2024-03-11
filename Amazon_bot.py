import requests
import time
import datetime
from bs4 import BeautifulSoup
from selenium import webdriver
import smtplib
import ssl

class AmazonBot:
    def __init__(self, mongodb_client,  server_smtp):
        self.amazon_header = {
            'authority': 'www.amazon.fr',
            'accept': 'text/html, */*; q=0.01',
            'accept-language': 'en-US,en;q=0.5',
            'cookie': 'session-id=257-9211973-0976268; session-id-time=2082787201l; i18n-prefs=EUR; ubid-acbfr=260-9842417-2475859; session-token=JP9RzoweqgRHPBGvIUL27RuhnEkAa/G3qiJnLOFr2x2C7Hu6JpvcEr4qU/E4+6xAFOXo86YIzfiR8uH6upCU+9QQ/JLRAIVo+Om2UfC12Klk9XyVwJfp09f8f29E10cT0W0T/EXsgScxvkz9VzorAHq78A5AAwtnUnucS9Rbw51M0HlQItJdLX8LzJM8AYv6wAuNqCKaDkwzrWniEimj6GuvU0TSLg1lu73JuzBJUbiq+jFeCdvm0WJTAXxE5JkPeKotqJJlgc0RE2PbvVC9vOXeES7ZIcRJ1/fy2WyvzKdHdFQqHud2rk1QWqm8ez8XXaLqqod0dUOf8bV4LT+9Fr3n2eEN+yME; csm-hit=tb:XR81AXZJS3J5RE17Q0R2+s-XR81AXZJS3J5RE17Q0R2|1702338613312&t:1702338613313&adb:adblk_yes',
            'referer': 'https://www.amazon.fr/Apple-AirPods-bo%C3%AEtier-charge-Dernier/dp/B07PZR3PVB/ref=sr_1_5?__mk_fr_FR=%C3%85M%C3%85%C5%BD%C3%95%C3%91&dchild=1&keywords=airpod&qid=1610634324&sr=8-5',
            'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Brave";v="120"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-ch-ua-platform-version': '"10.0.0"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'sec-gpc': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'x-requested-with': 'XMLHttpRequest',
        }
        
        self.mongodb_client = mongodb_client
        self.server_smtp = server_smtp
        self.driver = webdriver.Chrome()
        
    def get_product_titel(self, soup):
        try:
            return soup.find('span', {'id': 'productTitle'}).get_text().strip()
        except:
            return None
        
    def get_product_rating(self, soup):
        try:
            div_avg_cust_reviews = soup.find('div', {'id': 'averageCustomerReviews'})
            rating = div_avg_cust_reviews.find('span', {'class': 'a-icon-alt'}).get_text().strip()[0]
            return float(rating.replace(',', '.'))
        except:
            return None
        
    def get_product_nb_reviewers(self, soup):
        try:
            nb_reviewers= soup.find('span', {'id': 'acrCustomerReviewText'}).get_text().strip()
            return int(''.join(nb_reviewers.split()[:-1]))
        except:
            try:
                nb_reviewers= soup.find('span', {'id': 'acrCustomerReviewText'}).get_text().strip()
                return int(nb_reviewers.split(" ")[0].replace(",",""))
            except:
                return None
        
    def get_product_price(self, soup):
        try:
            price = soup.find('span',{'class': 'a-offscreen'}).get_text().strip()
            return float(price.replace("EUR", ""))
        except:
            try:
                price = soup.find('span',{'id': 'price'}).get_text().strip()
                return float(price.split()[0].replace(',' , '.')) 
            except:
                try:
                    return float(price.replace('€' , '').replace(',' , '.'))
                except:  
                    return None
          
    def get_product_data(self, product_url):
        r = requests.get(product_url, headers=self.amazon_header)
        soup = BeautifulSoup(r.content, 'html.parser')
        self.driver.get(product_url)
        soup = BeautifulSoup(self.driver.page_source,'html.parser')
        title = self.get_product_titel(soup)
        rating = self.get_product_rating(soup)
        nb_review =self.get_product_nb_reviewers(soup)
        price = self.get_product_price(soup)
        return {
            "url": product_url,
            "title": title,
            "rating": rating,
            "nb_review": nb_review,
            "price": price,
            "update_date": datetime.datetime.now()
        } 
    def scrap_urls(self):
        while True :
            product_urls=self.mongodb_client["amazon"]["product_urls"].find({
                "$or": [
                    {"updated_at":None},
                    {"updated_at":{"$lte":datetime.datetime.now() - datetime.timedelta(minutes=5)}}
                ]
            })
            for product_url in product_urls:
                print(product_url)
                print()
                data = self.get_product_data(product_url["url"])
                self.mongodb_client["amazon"]["product_data"].update_one({"url": product_url['url']}, {"$set": data}, upsert=True)
                self.mongodb_client["amazon"]["product_urls"].update_one({"url": product_url['url']}, {"$set": {
                    "update_at": datetime.datetime.now()
                }})

                try:
                    last_product_price = self.mongodb_client["amazon"]["product_prices"].find({"url": data["url"]}).sort([("created_at", -1)]).next()
                except:
                    last_product_price = None

                if last_product_price is None:
                    # Insert
                    self.mongodb_client["amazon"]["product_prices"].insert_one({
                        "url": product_url["url"],
                        "price": data["price"],
                        "created_at": datetime.datetime.now()
                    })
                elif last_product_price is not None and last_product_price['price'] != data['price']:
                    self.mongodb_client["amazon"]["product_prices"].insert_one({
                        "url": product_url['url'],
                        "price": data["price"],
                        "created_at": datetime.datetime.now()
                    })
                    if (type(data["price"]) is int or type(data["price"]) is float) and \
                        (type(last_product_price["price"]) is int or type(last_product_price["price"]) is float):
                        diff_price_percentage = ( 1 - data["price"] / last_product_price["price"]) * 100
                        print("Prices : ", data["price"], " \nLast product price : ",last_product_price["price"])  
                        print("Price drop percentage:", diff_price_percentage)

                        if diff_price_percentage > 0:
                            print("Sending email...")
                            message="""
                            Diminution du prix de %s%% pour le product %s.
                            Précédent prix: %s.
                            Nouveau prix: %s.
                            """ % (
                                diff_price_percentage,
                                product_url["url"],
                                last_product_price["price"],
                                data["price"]
                            )
                            message =message.encode('utf-8')
                            self.server_smtp.sendmail("charmaqh@gmail.com", "bh204607@gmail.com", message)
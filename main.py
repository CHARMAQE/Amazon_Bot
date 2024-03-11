import os
import smtplib, ssl
from dotenv import load_dotenv
from pymongo import MongoClient
from Amazon_bot import AmazonBot

load_dotenv()


try:
    client = MongoClient(
        "mongodb+srv://"+os.getenv("MONGODB_USERNAME")+
        ":"+os.getenv("MONGODB_PASSWORD")+
        "@"+os.getenv("MONGODB_DOMAIN")+
        "/"+os.getenv("MONGODB_DBNAME")+"?retryWrites=true&w=majority"
    )
    
    client.server_info()
except Exception as e:
    raise e

try:
    context = ssl.create_default_context()
    server = smtplib.SMTP_SSL('smtp.gmail.com',465,context=context)
    server.login(os.getenv("SENDER_EMAIL"),os.getenv("EMAIL_PASSWORD"))
except Exception as e:
    raise e
    
import sys

bot = AmazonBot(mongodb_client=client,server_smtp=server)
bot.scrap_urls()


sys.exit(0)

#product_urls = [
#   "https://www.amazon.fr/T12S-Transformation-semaines-minutes-d%C3%A9finitivement/dp/2035999642/ref=zg_bsnr_books_home_1?_encoding=UTF8&psc=1&refRID=71P5R2S30WR2EPDRPAP7",
#    "https://www.amazon.com/GYM-PEOPLE-Loose-fit-Sweatpants-Lined-Black/dp/B07YH9NDLW?ref_=Oct_DLandingS_D_f09b1168_1",
#    "https://www.amazon.fr/AmazonBasics-Paire-dhalt%C3%A8res-N%C3%A9opr%C3%A8ne-Noir/dp/B078XXSXRX?ref_=ast_sto_dp&th=1",
#    "https://www.amazon.fr/dp/B0CC9PCD64/ref=sspa_dk_detail_3?pd_rd_i=B0CC9PCD64&s=apparel&sp_csd=d2lkZ2V0TmFtZT1zcF9kZXRhaWw&th=1&psc=1",
#    "https://www.amazon.fr/AmazonBasics-Paire-dhalt%C3%A8res-N%C3%A9opr%C3%A8ne-Noir/dp/B078XXSXRX?ref_=ast_https://www.amazon.fr/dp/B0CC9PCD64/ref=sspa_dk_detail_3?pd_rd_i=B0CC9PCD64&s=apparel&sp_csd=d2lkZ2V0TmFtZT1zcF9kZXRhaWw&th=1&psc=1",
#    "https://www.amazon.fr/Schott-2190MAX-Jacket-Black-Medium/dp/B084N4PS9L?ref_=Oct_d_otopr_d_464849031_2&pd_rd_i=B084N4PS9L",
#    ]



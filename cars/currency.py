import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "webapp.settings")
import django
django.setup()
from django.core.management import call_command
from multiprocessing import *
from bs4 import BeautifulSoup
import schedule, time, requests
from .models import Currency, UniqueColor
import re

 
pattern = re.compile("^[a-zA-Zа-яА-ЯёЁ0-9\,\-\ ]+$")

async def start_process():
    p1 = Process(target=start_schedule, args=()).start()


def start_schedule():
    schedule.every().day.at("02:00").do(curr)
    #schedule.every(1115).seconds.do(curr)
    schedule.every(3600).seconds.do(get_unique)

    while True:
        schedule.run_pending()
        time.sleep(5)


def curr():
    url = 'http://auc.autocenter25.com/currency' 
    
    try:
        response = requests.get(url).json()
        #print("response =", response)
        
        currency = Currency(id=0)
        currency.date = response.get("date")
        currency.usd = response.get("usd")
        currency.eur = response.get("eur")
        currency.jpy = response.get("jpy")
        currency.krw = response.get("krw")
        currency.cny = response.get("cny") * 100
        currency.save()
    except Exception as e:
        print("Что-то не так с парсингом валют")
        print(e)


def get_unique():
    UniqueColor.objects.all().delete()

    for table in ["china", "main"]:
        for param in ["MARKA_NAME", "KPP", "PRIV", "COLOR"]:
            req = requests.get(
                f'http://78.46.90.228/api/?ip=45.84.177.55&code=A25nhGfE56Kd&sql=select+DISTINCT+{param}+from+{table}+WHERE+1+=+1+and+AUCTION+NOT+LIKE+"%USS%"+and+YEAR+>=+2015'
            ).text
            soup = BeautifulSoup(req, "lxml-xml")
            root = soup.find("aj")
            rows = root.find_all("row")
            
            if param == "MARKA_NAME":
                list_param = [i.find(param).text for i in rows]
            else:
                list_param = [i.find(param).text for i in rows if pattern.search(i.find(param).text) is not None]
            
            list_param = sorted(list_param)
            for i, _key in enumerate(list_param):
                col = UniqueColor.objects.create(name=_key, type_of_unique=param, table=table)
                col.save()
                    

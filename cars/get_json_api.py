from bs4 import BeautifulSoup
from .sub_fun import calc_price
from requests import get
from .models import Currency


def get_car(html_text: str, table: str):
    currency = Currency.objects.all()[0]

    soup = BeautifulSoup(html_text, "lxml-xml")
    root = soup.find("aj")
    rows = root.find_all("row")
    list_car = []

    for row in rows:
        price_avg = int(row.find("AVG_PRICE").text)
        price_start = int(row.find("START").text)
        price_finish = int(row.find("FINISH").text)
        
        if price_avg > 0:
            price = price_avg
        elif price_avg == 0 and price_finish > 0:
            price = price_finish
        elif price_avg == 0 and price_finish == 0 and price_start > 0:
            price = price_finish
        else:
            price = 0  
            
        car = {
            "api_id": row.find("ID").text,
            "brand": row.find("MARKA_NAME").text,
            "model": row.find("MODEL_NAME").text,
            "year": row.find("YEAR").text,
            "body_type": row.find("KUZOV").text,
            "color": row.find("COLOR").text,
            "transmission": row.find("KPP").text,
            "engine_volume": row.find("ENG_V").text,
            "drive": row.find("PRIV").text,
            "mileage": row.find("MILEAGE").text,
        }
        try:     
            car["price"], car["inside"], car["outside"], car["toll"] = calc_price(
                price=price,
                currency=currency,
                year=int(row.find("YEAR").text),
                volume=int(row.find("ENG_V").text),
                table=table,
            )
        except:
            car["price"] = 0
        car["photos"] = row.find("IMAGES").text.replace("=50", "").split("#")
        list_car.append(car)

    return list_car


def get_count(html_text: str):
    soup = BeautifulSoup(html_text, "lxml-xml")
    root = soup.find("aj")
    rows = root.find("row")
    count = int(rows.find("TAG0").text)
    return count

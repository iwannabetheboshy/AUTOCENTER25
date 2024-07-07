import asyncio
from django.core.management.base import BaseCommand
from bs4 import BeautifulSoup
from django.core.files import File
from aiohttp import ClientSession
from urllib.error import HTTPError
import logging
from tempfile import NamedTemporaryFile
from asgiref.sync import sync_to_async
from cars.sub_fun import calc_price
from cars.models import (
    PhotoCars,
    BodyType,
    Transmission,
    TypeEngine,
    Drive,
    Color,
    CarJapan,
    CarChina,
)

URL_JAPAN = 'http://78.46.90.228/api/?ip=45.84.177.55&code=A25nhGfE56Kd&sql=select+*+from+main+WHERE+1+=+1+and+AUCTION+NOT+LIKE+"%USS%"+and+YEAR+>=+2008+limit+{},25'
URL_CHINA = 'http://78.46.90.228/api/?ip=45.84.177.55&code=A25nhGfE56Kd&sql=select+*+from+china+WHERE+1+=+1+and+AUCTION+NOT+LIKE+"%USS%"+and+YEAR+>=+2015+limit+{},25'


async def fetch(session, url):
    async with session.get(url) as response:
        return await response.text(encoding="windows-1251")


async def get_car(session, table: str = "", i=1):
    perpage = i * 25
    url = (
        URL_CHINA.format(perpage)
        if table == "china"
        else URL_JAPAN.format(perpage)
    )
    response_text = await fetch(session, url)

    try:
        soup = BeautifulSoup(response_text, "lxml-xml")
        root = soup.find("aj")
        rows = root.find_all("row")
    except Exception as e:
        logging.error(f"Error parsing XML: {e}")
        logging.debug(f"Response text: {response_text}")
        return

    for row in rows:
        try:
            logging.debug(f"Processing row: {row}")

            api_id_element = row.find("ID")
            brand_element = row.find("MARKA_NAME")
            model_element = row.find("MODEL_NAME")
            year_element = row.find("YEAR")
            body_type_name_element = row.find("KUZOV")
            transmission_name_element = row.find("KPP")
            fuel_type_name_element = row.find("PRIV")
            engine_volume_element = row.find("ENG_V")
            drive_name_element = row.find("PRIV")
            color_element = row.find("COLOR")
            mileage_element = row.find("MILEAGE")
            price_element = row.find("AVG_PRICE")
            image_urls_element = row.find("IMAGES")

            elements = {
                "ID": api_id_element,
                "MARKA_NAME": brand_element,
                "MODEL_NAME": model_element,
                "YEAR": year_element,
                "KUZOV": body_type_name_element,
                "KPP": transmission_name_element,
                "PRIV": fuel_type_name_element,
                "ENG_V": engine_volume_element,
                "COLOR": color_element,
                "MILEAGE": mileage_element,
                "AVG_PRICE": price_element,
                "IMAGES": image_urls_element,
            }
            print(elements)

            for key, value in elements.items():
                if value is not None:
                    logging.debug(f"{key}: {value.text}")
                else:
                    logging.debug(f"{key}: None")

            if not all(
                [
                    api_id_element,
                    brand_element,
                    model_element,
                    year_element,
                    body_type_name_element,
                    transmission_name_element,
                    fuel_type_name_element,
                    drive_name_element,
                ]
            ):
                logging.error(f"Missing essential element in row: {row}")
                continue

            api_id = api_id_element.text
            brand = brand_element.text
            model = model_element.text
            year = int(year_element.text)
            body_type_name = body_type_name_element.text
            transmission_name = transmission_name_element.text
            fuel_type_name = fuel_type_name_element.text
            drive_name = drive_name_element.text.split(",")[-1]

            if engine_volume_element is not None:
                engine_volume_text = engine_volume_element.text
                logging.debug(
                    f"Engine volume text: {engine_volume_text}, type: {type(engine_volume_text)}"
                )
                if (
                    isinstance(engine_volume_text, str)
                    and engine_volume_text.replace(",", "").isdigit()
                ):
                    engine_volume = int(engine_volume_text.replace(",", ""))
                else:
                    logging.error(
                        f"Invalid engine volume: {engine_volume_text}"
                    )
                    engine_volume = 0
            else:
                engine_volume = 0

            color_name = (
                color_element.text
                if color_element and color_element.text
                else "Unknown"
            ).upper()
            mileage = (
                int(mileage_element.text.replace(",", ""))
                if mileage_element
                and isinstance(mileage_element.text, str)
                and mileage_element.text.replace(",", "").isdigit()
                else 0
            )

            if price_element is not None:
                price_text = price_element.text
                logging.debug(
                    f"Price text: {price_text}, type: {type(price_text)}"
                )
                price = calc_price(
                    price=(
                        float(price_text.replace(",", ""))
                        if isinstance(price_text, str)
                        and price_text.replace(",", "")
                        .replace(".", "")
                        .isdigit()
                        else 0
                    ),
                    currency={"jpy": 100, "cny": 100, "eur": 100},
                    year=year,
                    volume=engine_volume,
                    table=table,
                )
            else:
                price = 0.0

            image_urls = (
                image_urls_element.text.split("#")
                if image_urls_element
                and isinstance(image_urls_element.text, str)
                else []
            )

            body_type, _ = await sync_to_async(BodyType.objects.get_or_create)(
                name=body_type_name
            )
            transmission, _ = await sync_to_async(
                Transmission.objects.get_or_create
            )(name=transmission_name)
            fuel_type, _ = await sync_to_async(
                TypeEngine.objects.get_or_create
            )(name=fuel_type_name)
            drive, _ = await sync_to_async(Drive.objects.get_or_create)(
                name=drive_name
            )
            color, _ = await sync_to_async(Color.objects.get_or_create)(
                name=color_name
            )

            car_model = CarChina if table == "china" else CarJapan
            car = await sync_to_async(car_model.objects.create)(
                api_id=api_id,
                brand=brand,
                model=model,
                year=year,
                body_type=body_type,
                transmission=transmission,
                fuel_type=fuel_type,
                engine_volume=engine_volume,
                drive=drive,
                color=color,
                mileage=mileage,
                price=price,
            )

            for image_url in image_urls:
                try:
                    image_url = image_url.replace("=50", "")
                    logging.debug(
                        f"Attempting to download image from URL: {image_url}"
                    )
                    img_temp = NamedTemporaryFile(delete=True)
                    async with session.get(image_url) as uo:
                        img_temp.write(await uo.read())
                    img_temp.flush()
                    photo = PhotoCars()
                    await sync_to_async(photo.image.save)(
                        f"{api_id}.jpg", File(img_temp), save=True
                    )
                    await sync_to_async(car.photos.add)(photo)
                except HTTPError as e:
                    logging.error(
                        f"HTTP Error saving image: {e.code} for URL: {image_url}"
                    )
                except Exception as e:
                    logging.error(f"Error saving image: {e}")

            await sync_to_async(car.save)()
        except Exception as e:
            logging.error(f"Error processing row: {e}")
            logging.debug(f"Row data: {row}")
            logging.debug(
                f"Row contents: {[(child.name, child.text) for child in list(row) if hasattr(child, 'name') and child.name is not None]}"
            )


async def mock():
    async with ClientSession() as session:
        tasks = []
        for i in range(1, 20):
            tasks.append(get_car(session, i=i))
            # tasks.append(get_car(session, table="china", i=i))
        await asyncio.gather(*tasks)


class Command(BaseCommand):
    help = "Добавляет данные с API"

    def handle(self, *args, **kwargs):
        asyncio.run(mock())

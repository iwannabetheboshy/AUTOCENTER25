from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.views.generic.list import ListView
from requests import get
from .paginator import get_page
from .models import (
    FeedBack,
    CarKorea,
    CarChina,
    CarJapan,
    CarMainPage,
    Reviews
)
from .base_view import (
    FilteredCarListView,
    CarDetailView,
    CarKoreaMainView,
)
from .forms import (
    FeedbackForm,
    CarChinaFilterForm,
    CarJapanFilterForm,
    CarKoreaFilterForm,
)
import asyncio
from django.views.decorators.http import require_GET
from cars.currency import start_process
asyncio.run(start_process())


@require_GET
def robots_txt(request):
    lines = [
        "User-agent: Yandex",
        "Allow: /",
        "Allow: /cars_japan/",
        "Allow: /cars_china/",
        "Allow: /cars_korea/",
        "Allow: /article/1/",
        "Allow: /article/2/",
        "Allow: /article/3/",
        "",
        "Disallow: /car_japan/*",
        "Disallow: /car_china/*",
        "Disallow: /car_korea/*",
        "Disallow: /about_us/",
        "",
        "User-agent: *",
        "Allow: /",
        "Allow: /cars_japan/",
        "Allow: /cars_china/",
        "Allow: /cars_korea/",
        "Allow: /article/1/",
        "Allow: /article/2/",
        "Allow: /article/3/",
        "",
        "Disallow: /car_japan/*",
        "Disallow: /car_china/*",
        "Disallow: /car_korea/*",
        "Disallow: /about_us/",        
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")


def main(request):
    data = {"feedbackForm": FeedbackForm(), "cars": CarMainPage.objects.all(), "reviews": Reviews.objects.all()}
    return render(request, "main/index.html", data)


def about_us(request):
    data = {"feedbackForm": FeedbackForm()}
    return render(request, "main/about_us.html", data)


def article_1(request):
    return render(request, "main/articles_1.html")
def article_2(request):
    return render(request, "main/articles_2.html")
def article_3(request):
    return render(request, "main/articles_3.html")

@csrf_exempt
def sendFeedBack(request):
    if request.method == "POST":
        form = FeedbackForm(request.POST)
        print(form)
        if form.is_valid():
            f = FeedBack(
                name=form.cleaned_data["name"],
                number=form.cleaned_data["number"],
                message=form.cleaned_data["message"],
            )
            f.save()
            # print(f)
            name = form.cleaned_data["name"]
            number = form.cleaned_data["number"]
            message = form.cleaned_data["message"]
            get(
                "https://api.telegram.org/bot7308037244:AAEphpg72xfYk_MdRZ1EzuGZQq6i2FuTmDw/sendmessage?chat_id={user_id}&text={text}".format(
                    text=f"Имя: {name}\nТелефон: {number}\nЗапрос: {message}",
                    user_id=629793380,
                )
            )
            #get(
            #    "https://api.telegram.org/bot7308037244:AAEphpg72xfYk_MdRZ1EzuGZQq6i2FuTmDw/sendmessage?chat_id={user_id}&text={text}".format(
            #        text=f"Имя: {name}\nТелефон: {number}\nЗапрос: {message}",
            #        user_id=6600969548,
            #    )
            #)
            #get(
            #    "https://autocenter.bitrix24.ru/rest/1/5gyn8c68hatc27yv/crm.lead.add.json"\
            #    "?FIELDS[NAME]={name}"
            #    "&FIELDS[PHONE][0][VALUE]={number}"
            #    "&FIELDS[TITLE]=Увидомление%20с%20сайта"
            #    "&FIELDS[COMMENTS]={message}".format(
            #        name=name,
            #        number=number,
            #        message=message,
            #    )
            #)
    return HttpResponse("Заявка отправлена! Мы скоро перезвоним вам")


class CarsKorea(ListView):
    model = CarKorea
    form_filter = CarKoreaFilterForm
    template_name = "base/catalog.html"
    context_object_name = "cars"
    link_url = "car_list_korea"
    title = "Каталог Корея"
    car_link = "car_korea"
    url_api = "/api/cars/korea/"
    paginate_by = 8

    def get_queryset(self):
        queryset = super().get_queryset().order_by("id")
        form = self.filter_form()

        if form.is_valid():
            if form.cleaned_data["brand"]:
                queryset = queryset.filter(brand=form.cleaned_data["brand"])
            if form.cleaned_data["model"]:
                queryset = queryset.filter(model=form.cleaned_data["model"])
            if form.cleaned_data["mileage_min"]:
                queryset = queryset.filter(
                    mileage__gte=form.cleaned_data["mileage_min"].replace(
                        " ", ""
                    )
                )
            if form.cleaned_data["mileage_max"]:
                queryset = queryset.filter(
                    mileage__lte=form.cleaned_data["mileage_max"].replace(
                        " ", ""
                    )
                )
            if form.cleaned_data["year_min"]:
                queryset = queryset.filter(
                    year__gte=form.cleaned_data["year_min"]
                )
            if form.cleaned_data["year_max"]:
                queryset = queryset.filter(
                    year__lte=form.cleaned_data["year_max"]
                )
            if form.cleaned_data["engine_volume_min"]:
                queryset = queryset.filter(
                    engine_volume__gte=form.cleaned_data[
                        "engine_volume_min"
                    ].replace(" ", "")
                )
            if form.cleaned_data["engine_volume_max"]:
                queryset = queryset.filter(
                    engine_volume__lte=form.cleaned_data[
                        "engine_volume_max"
                    ].replace(" ", "")
                )
            #if form.cleaned_data["transmission"]:
            #    queryset = queryset.filter(
            #        transmission=form.cleaned_data["transmission"]
            #    )
            if form.cleaned_data["drive"]:
                queryset = queryset.filter(drive=form.cleaned_data["drive"])
            if form.cleaned_data["color"]:
                queryset = queryset.filter(color=form.cleaned_data["color"])

        for i in queryset:
            i.api_id = i.id

        return queryset

    def filter_form(self):
        return self.form_filter(self.request.GET or None)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["filter_form"] = self.filter_form()
        context["link_url"] = self.link_url
        context["feedbackForm"] = FeedbackForm()
        context["title"] = self.title
        context["car_link"] = self.car_link
        context["url_api"] = self.url_api

        queryset = self.get_queryset()
        paginator = self.get_paginator(queryset, self.paginate_by)
        page_number = self.request.GET.get("page", 1)
        page_obj = get_page(paginator=paginator, page_number=page_number)

        context["page_obj"] = page_obj
        context["is_paginated"] = page_obj.has_other_pages()
        context["cars"] = page_obj.object_list

        return context


class CarsChina(FilteredCarListView):
    form_filter = CarChinaFilterForm
    link_url = "car_list_china"
    title = "Каталог Китай"
    car_link = "car_china"
    table = "china"
    url_api = "/api/cars/china/"


class CarsJapan(FilteredCarListView):
    #url_api_now = 'http://78.46.90.228/api/?ip={ip}&code=A25nhGfE56Kd&sql=select+*+from+{table}+WHERE+1+=+1+and+AUCTION+NOT+LIKE+"%USS%"+and+YEAR+>=+2015+and+AVG_PRICE+>=+1+{filter}limit+{offset},{limit}'
    #url_api_count = 'http://78.46.90.228/api/?ip={ip}&code=A25nhGfE56Kd&sql=select+count(*)+from+{table}+WHERE+1+=+1+and+AUCTION+NOT+LIKE+"%USS%"+and+YEAR+>=+2015+and+AVG_PRICE+>=+1+{filter}'
    form_filter = CarJapanFilterForm
    link_url = "car_list_japan"
    title = "Каталог Япония"
    table = "main"
    car_link = "car_japan"
    url_api = "/api/cars/japan/"


class CarKoreaDetailView(CarKoreaMainView):
    model = CarKorea
    slug_field = "pk"
    slug_url_kwarg = "pk"


class CarMainDetailView(CarKoreaMainView):
    model = CarMainPage
    slug_field = "pk"
    slug_url_kwarg = "pk"


class CarChinaDetailView(CarDetailView):
    model = CarChina
    slug_field = "api_id"
    slug_url_kwarg = "api_id"
    country = "Китай"


class CarJapanDetailView(CarDetailView):
    model = CarJapan
    slug_field = "api_id"
    slug_url_kwarg = "api_id"
    country = "Япония"

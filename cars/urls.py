from django.urls import path
from .views import (
    CarsKorea,
    CarsChina,
    CarsJapan,
    main,
    sendFeedBack,
    CarMainDetailView,
    CarChinaDetailView,
    CarJapanDetailView,
    CarKoreaDetailView,
    about_us,
    article_1,
    article_2,
    article_3,
    robots_txt
)
from .view_api import car_china, car_main, car_korea


urlpatterns_api = [
    path(
        "api/cars/japan/<str:brand>/",
        car_main,
        name="car_japan_list",
    ),
    path(
        "api/cars/china/<str:brand>/",
        car_china,
        name="car_china_list",
    ),
    path(
        "api/cars/korea/<str:brand>/",
        car_korea,
        name="car_korea_list",
    ),
]

urlpatterns = [
    path("", main, name="main"),
    path("feedback/", sendFeedBack, name="send_feed_back"),
    path("cars_korea/", CarsKorea.as_view(), name="car_list_korea"),
    path("cars_china/", CarsChina.as_view(), name="car_list_china"),
    path("cars_japan/", CarsJapan.as_view(), name="car_list_japan"),
    path(
        "car_china/<str:api_id>",
        CarChinaDetailView.as_view(),
        name="car_china",
    ),
    path("car_korea/<int:pk>", CarKoreaDetailView.as_view(), name="car_korea"),
    path("cars/<int:pk>", CarMainDetailView.as_view(), name="car_main"),
    path(
        "car_japan/<str:api_id>",
        CarJapanDetailView.as_view(),
        name="car_japan",
    ),
    path("about_us/", about_us, name="about_us"),
    path("article/1", article_1, name="article_1"),
    path("article/2", article_2, name="article_2"),
    path("article/3", article_3, name="article_3"),
    path("robots.txt", robots_txt, name='robots_txt'),
] + urlpatterns_api

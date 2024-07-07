from rest_framework import generics
from rest_framework.response import Response
from .models import CarJapan, CarChina, CarKorea
from .sub_fun import unique_param_with_brand
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view


@api_view(["GET"])
def car_main(request, brand):
    data = unique_param_with_brand("MODEL_NAME", "main", brand)
    return Response(data, status=status.HTTP_200_OK)


@api_view(["GET"])
def car_china(request, brand):
    data = unique_param_with_brand("MODEL_NAME", "china", brand)
    return Response(data, status=status.HTTP_200_OK)


@api_view(["GET"])
def car_korea(request, brand):
    data = list(
        set(
            [
                i.get("model")
                for i in CarKorea.objects.filter(brand__iexact=brand)
                .values("model")
                .distinct()
            ]
        )
    )
    return Response(data, status=status.HTTP_200_OK)

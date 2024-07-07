import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _
from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.urls import reverse


class PhotoCars(models.Model):
    image = models.ImageField(upload_to="photos/")

    def save(self, *args, **kwargs):
        name = str(uuid.uuid1())
        img = Image.open(self.image)
        img_io = BytesIO()
        img.save(img_io, format="WebP")
        img_file = InMemoryUploadedFile(
            img_io, None, f"{name}.webp", "image/webp", img_io.tell(), None
        )
        self.image.save(f"{name}.webp", img_file, save=False)

        super(PhotoCars, self).save(*args, **kwargs)

    class Meta:
        verbose_name = _("Фото машины")
        verbose_name_plural = _("Фото машин")

    def __str__(self):
        return f"{self.image}"


class Reviews(models.Model):
    class Meta:
        verbose_name = _("Отзыв")
        verbose_name_plural = _("Отзывы")

    name = models.CharField(
        max_length=200,
        verbose_name=_("Имя Фамилия"),
    )

    text_review = models.TextField(verbose_name=_("Коментарий пользователя"))

    icon_user = models.ImageField(
        upload_to="user/phoro_user",
        null=True,
        verbose_name=_("Фотографии пользователя"),
    )

    reviews_date = models.DateField(
        verbose_name=_("Дата отзыва"),
        help_text=_("Уже загруженные фотографии не нужно добовлять заново"),
    )
    
    num_view = models.IntegerField(
        verbose_name=_("Номер отображения"),
        help_text=_("Каким по очереди отображать?"),
        default=0,
    )
    
    image1 = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        verbose_name=_("Фотография к отзыву 1"),
    )
    
    image2 = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        verbose_name=_("Фотография к отзыву 2"),
    )

    def save(self, *args, **kwargs):
        if self.icon_user:
            name = str(uuid.uuid1())
            img = Image.open(self.icon_user)
            img_io = BytesIO()
            img.save(img_io, format="WebP")
            img_file = InMemoryUploadedFile(
                img_io, None, f"{name}.webp", "image/webp", img_io.tell(), None
            )
            self.icon_user.save(f"{name}.webp", img_file, save=False)

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name}"


class FeedBack(models.Model):
    name = models.CharField("Имя", max_length=50)
    number = models.CharField("Номер телефона", max_length=20)
    message = models.TextField("Сообщение", blank=True, null=True)

    class Meta:
        verbose_name = "заявка"
        verbose_name_plural = "Заявки"

    def __str__(self):
        return f"{self.name} {self.number}"

    class Meta:
        verbose_name = "Завяка"
        verbose_name_plural = "Заявки"


class BodyType(models.Model):
    name = models.CharField(
        verbose_name=_("Названия типо кузова"), max_length=100
    )

    class Meta:
        verbose_name = _("Тип кузовова")
        verbose_name_plural = _("Типы кузова")

    def __str__(self):
        return f"{self.name}"


class Transmission(models.Model):
    name = models.CharField(verbose_name=_("КПП название"), max_length=100)

    class Meta:
        verbose_name = _("Тип КПП")
        verbose_name_plural = _("Типы КПП")

    def __str__(self):
        return f"{self.name}"


class TypeEngine(models.Model):
    name = models.CharField(
        verbose_name=_("Тип двигателя ( значение )"), max_length=100
    )

    class Meta:
        verbose_name = _("Тип двигателя")
        verbose_name_plural = _("Типы двигателя")

    def __str__(self):
        return f"{self.name}"


class Drive(models.Model):
    name = models.CharField(verbose_name=_("Название привода"), max_length=100)

    class Meta:
        verbose_name = _("Тип привода")
        verbose_name_plural = _("Типы приводов")

    def __str__(self):
        return f"{self.name}"


class Color(models.Model):
    class Meta:
        verbose_name = _("Цвет для машины")
        verbose_name_plural = _("Цвета для машин")

    name = models.CharField(verbose_name=_("Название цвета"), max_length=100)

    def __str__(self):
        return f"{self.name}"


class CarJapan(models.Model):

    class Meta:
        verbose_name = "Авто Япония"
        verbose_name_plural = "Авто Япония"

    api_id = models.CharField(
        max_length=100,
        verbose_name=_("ID в API"),
        help_text=_("Параметр нельзя менять"),
    )
    brand = models.CharField(
        max_length=100,
        verbose_name=_("Бренд"),
        help_text=_("Впишите название бренда"),
    )
    model = models.CharField(
        max_length=150,
        verbose_name=_("Модель"),
        help_text=_("Впишите название модели"),
    )
    year = models.IntegerField(
        verbose_name=_("Год"), help_text=_("Впишите год автомабиля")
    )
    body_type = models.ForeignKey(
        BodyType, on_delete=models.CASCADE, verbose_name=_("Тип кузова")
    )
    transmission = models.ForeignKey(
        Transmission, on_delete=models.CASCADE, verbose_name=_("Тип КПП")
    )
    fuel_type = models.ForeignKey(
        TypeEngine, on_delete=models.CASCADE, verbose_name=_("Тип двигателя")
    )
    engine_volume = models.IntegerField(
        verbose_name=_("Объяем двигателя"),
        help_text=_("Впишите объяем двигателя"),
    )
    drive = models.ForeignKey(
        Drive, on_delete=models.CASCADE, verbose_name=_("Тип привода")
    )
    color = models.ForeignKey(
        Color, on_delete=models.CASCADE, verbose_name=_("Цвет")
    )
    mileage = models.IntegerField()
    price = models.DecimalField(max_digits=100, decimal_places=2)

    photos = models.ManyToManyField(
        PhotoCars, null=True, verbose_name=_("Фотографии авто")
    )

    def __str__(self):
        return f"{self.brand} {self.model} ({self.year}) {self.color}- {self.price}"

    def get_absolute_url(self):

        return reverse("car_japan", kwargs={"api_id": self.api_id})


class CarChina(models.Model):

    class Meta:
        verbose_name = "Авто Китай"
        verbose_name_plural = "Авто Китай"

    api_id = models.CharField(
        max_length=100,
        verbose_name=_("ID в API"),
        help_text=_("Параметр нельзя менять"),
    )

    brand = models.CharField(
        max_length=100,
        verbose_name=_("Бренд"),
        help_text=_("Впишите название бренда"),
    )
    model = models.CharField(
        max_length=150,
        verbose_name=_("Модель"),
        help_text=_("Впишите название модели"),
    )
    year = models.IntegerField(
        verbose_name=_("Год"), help_text=_("Впишите год автомабиля")
    )
    body_type = models.ForeignKey(
        BodyType, on_delete=models.CASCADE, verbose_name=_("Тип кузова")
    )
    transmission = models.ForeignKey(
        Transmission, on_delete=models.CASCADE, verbose_name=_("Тип КПП")
    )
    fuel_type = models.ForeignKey(
        TypeEngine, on_delete=models.CASCADE, verbose_name=_("Тип двигателя")
    )
    engine_volume = models.IntegerField(
        verbose_name=_("Объяем двигателя"),
        help_text=_("Впишите объяем двигателя"),
    )
    drive = models.ForeignKey(
        Drive, on_delete=models.CASCADE, verbose_name=_("Тип привода")
    )
    color = models.ForeignKey(
        Color, on_delete=models.CASCADE, verbose_name=_("Цвет")
    )
    mileage = models.IntegerField()
    price = models.IntegerField()

    photos = models.ManyToManyField(
        PhotoCars, null=True, verbose_name=_("Фотографии авто")
    )

    def __str__(self):
        return f"{self.brand} {self.model} ({self.year}) {self.color}- {self.price}"

    def get_absolute_url(self):
        return reverse("car_china", kwargs={"api_id": self.api_id})


class CarKorea(models.Model):

    class Meta:
        verbose_name = "Авто Корея"
        verbose_name_plural = "Авто Корея"

    brand = models.CharField(
        max_length=100,
        verbose_name=_("Бренд"),
        help_text=_("Впишите название бренда"),
    )
    model = models.CharField(
        max_length=150,
        verbose_name=_("Модель"),
        help_text=_("Впишите название модели"),
    )
    year = models.IntegerField(
        verbose_name=_("Год"), help_text=_("Впишите год автомабиля")
    )
    fuel_type = models.ForeignKey(
        TypeEngine, on_delete=models.CASCADE, verbose_name=_("Тип двигателя")
    )
    engine_volume = models.IntegerField(
        verbose_name=_("Объяем двигателя"),
        help_text=_("Впишите объяем двигателя"),
    )
    drive = models.ForeignKey(
        Drive, on_delete=models.CASCADE, verbose_name=_("Тип привода")
    )
    color = models.ForeignKey(
        Color, on_delete=models.CASCADE, verbose_name=_("Цвет")
    )
    mileage = models.IntegerField()
    price = models.IntegerField()

    photos = models.ManyToManyField(
        PhotoCars, null=True, verbose_name=_("Фотографии авто")
    )

    def __str__(self):
        return f"{self.brand} {self.model} ({self.year}) {self.color}- {self.price}"

    def get_absolute_url(self):
        return reverse("car_korea", kwargs={"pk": self.pk})


class CarMainPage(models.Model):

    class Meta:
        verbose_name = "Авто Главная Страница"
        verbose_name_plural = "Авто Главная Страница"

    brand = models.CharField(
        max_length=100,
        verbose_name=_("Бренд"),
        help_text=_("Впишите название бренда"),
    )
    model = models.CharField(
        max_length=150,
        verbose_name=_("Модель"),
        help_text=_("Впишите название модели"),
    )
    year = models.IntegerField(
        verbose_name=_("Год"), help_text=_("Впишите год автомабиля")
    )
    body_type = models.ForeignKey(
        BodyType, on_delete=models.CASCADE, verbose_name=_("Тип кузова")
    )
    transmission = models.ForeignKey(
        Transmission, on_delete=models.CASCADE, verbose_name=_("Тип КПП")
    )
    fuel_type = models.ForeignKey(
        TypeEngine, on_delete=models.CASCADE, verbose_name=_("Тип двигателя")
    )
    engine_volume = models.IntegerField(
        verbose_name=_("Объяем двигателя"),
        help_text=_("Впишите объяем двигателя"),
    )
    drive = models.ForeignKey(
        Drive, on_delete=models.CASCADE, verbose_name=_("Тип привода")
    )
    color = models.ForeignKey(
        Color, on_delete=models.CASCADE, verbose_name=_("Цвет")
    )
    mileage = models.IntegerField()
    price = models.IntegerField()

    photos = models.ManyToManyField(
        PhotoCars, null=True, verbose_name=_("Фотографии авто")
    )

    def __str__(self):
        return f"{self.brand} {self.model} ({self.year}) {self.color}- {self.price}"

    def get_absolute_url(self):
        return reverse("car_main_page/", kwargs={"pk": self.pk})


class Currency(models.Model):

    class Meta:
        verbose_name = "Валюты"
        verbose_name_plural = "Валюты"
    
    date = models.CharField(
        max_length=100,
        verbose_name=_("Дата парсинга"),
    )
    
    usd = models.FloatField(
        null=True,
        blank=True,
        default=None,
        verbose_name=_("USD"),
    )
    
    eur = models.FloatField(
        null=True,
        blank=True,
        default=None,
        verbose_name=_("EUR"),
    )
    
    jpy = models.FloatField(
        null=True,
        blank=True,
        default=None,
        verbose_name=_("JPY"),
    )
    
    krw = models.FloatField(
        null=True,
        blank=True,
        default=None,
        verbose_name=_("KRW"),
    )
    
    cny = models.FloatField(
        null=True,
        blank=True,
        default=None,
        verbose_name=_("CNY"),
    )
    
    def __str__(self):
        return f"{self.date}"


class UniqueColor(models.Model):
    class Meta:
        verbose_name = _("Уникальные цвета авто")
        verbose_name_plural = _("Уникальные цвета авто")

    name = models.CharField(verbose_name=_("Элемент"), max_length=100, default="")
    type_of_unique = models.CharField(verbose_name=_("Тип"), max_length=100, default="")
    table = models.CharField(verbose_name=_("Таблица"), max_length=100, default="")

    def __str__(self):
        return f"{self.name} {self.type_of_unique} {self.table}"
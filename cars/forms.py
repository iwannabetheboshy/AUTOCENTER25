import re

from django.forms import ModelForm, TextInput, Textarea
from django import forms

from .models import (
    FeedBack,
    Transmission,
    Drive,
    Color,
    CarKorea,
)
from .sub_fun import get_all_model, get_unique_param


class FeedbackForm(ModelForm):
    class Meta:
        model = FeedBack
        fields = ["name", "number", "message"]

        widgets = {
            "name": TextInput(
                attrs={
                    "class": "form-control fb_name",
                    "placeholder": "Введите имя",
                    "required": "true",
                    "title": "Используйте только буквы",
                }
            ),
            "number": TextInput(
                attrs={
                    "class": "form-control fb_phone",
                    "required": "true",
                    "type": "tel",
                    "placeholder": "+7 ",
                    "pattern": r"^\+7 \(\d{3}\) \d{3}-\d{2}-\d{2}$",
                    "title": "+7 (XXX) XXX-XX-XX",
                }
            ),
            "message": Textarea(
                attrs={
                    "class": "form-control-area",
                    "placeholder": "Введите текст сообщения",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super(FeedbackForm, self).__init__(*args, **kwargs)

        # Удаление id для каждого поля
        for field_name in self.fields:
            self.fields[field_name].widget.attrs["id"] = ""


class CarFilterForm(forms.Form):
    brand = forms.ChoiceField(
        choices=[],
        required=False,
        label="Марка",
        widget=forms.Select(
            attrs={"class": "form-control hidden-select"},
        ),
    )
    model = forms.ChoiceField(
        choices=[],
        required=False,
        label="Модель",
        widget=forms.Select(
            attrs={"class": "form-control hidden-select"},
        ),
    )

    mileage_min = forms.Field(
        required=False,
        label="Пробег от",
        widget=forms.TextInput(
            attrs={
                "class": "form-control discharges",
                "placeholder": "Пробег от, км",
                "type": "number",
                "min": "0",
                "step": "10000",
                "onkeypress": "limitCharacters(this, 6, event)"
            },
        ),
    )
    mileage_max = forms.Field(
        required=False,
        label="до",
        widget=forms.TextInput(
            attrs={
                "class": "form-control discharges", 
                "placeholder": "до", 
                "type": "number",
                "min": "0",
                "step": "10000",
                "onkeypress": "limitCharacters(this, 6, event)"
            },
        ),
    )

    year_min = forms.Field(
        required=False,
        label="Год от",
        widget=forms.TextInput(
            attrs={
                "class": "form-control", 
                "placeholder": "Год от", 
                "type": "number",
                "min": "2015",
                "max": "2024",
                "step": "1",
                "onkeypress": "limitCharacters(this, 4, event)"
            },
        ),
    )
    year_max = forms.Field(
        required=False,
        label="до",
        widget=forms.TextInput(
            attrs={
                "class": "form-control", 
                "placeholder": "до", 
                "type": "number",
                "min": "2015",
                "max": "2024",
                "step": "1",
                "onkeypress": "limitCharacters(this, 4, event)"
            },
        ),
    )

    engine_volume_min = forms.Field(
        required=False,
        label="Объем от",
        widget=forms.TextInput(
            attrs={
                "class": "form-control discharges",
                "placeholder": "Объем от, cc",
                "type": "number",
                "min": "0",
                "max": "10000",
                "step": "100",
                "onkeypress": "limitCharacters(this, 4, event)"
            },
        ),
    )
    engine_volume_max = forms.Field(
        required=False,
        label="до",
        widget=forms.TextInput(
            attrs={
                "class": "form-control discharges",
                "placeholder": "до",
                "type": "number",
                "min": "0",
                "max": "10000",
                "step": "100",
                "onkeypress": "limitCharacters(this, 4, event)"
            },
        ),
    )

    transmission = forms.ChoiceField(
        choices=[],
        required=False,
        label="Тип КПП",
        widget=forms.Select(
            attrs={
                "class": "form-control hidden-select"
            },
        ),
    )

    drive = forms.ChoiceField(
        choices=[],
        required=False,
        label="Тип привода",
        widget=forms.Select(
            attrs={
                "class": "form-control hidden-select"
            },
        ),
    )

    color = forms.ChoiceField(
        choices=[],
        required=False,
        label="Цвет",
        widget=forms.Select(
            attrs={
                "class": "form-control hidden-select"
            },
        ),
    )

    def is_valid(self):
        valid = super(CarFilterForm, self).is_valid()
        if not valid:
            print(self.errors)
            if "model" in self.errors:
                model = self.errors["model"]
                match = re.search(
                    r"Выберите корректный вариант\. (.*?) нет среди допустимых значений\.",
                    model[0],
                )
                value = match.group(1) if match else None
                # value["model"] = value
                self.cleaned_data["model"] = value
                print(value)
                del self.errors["model"]

            if "color" in self.errors:
                color = self.errors["color"]
                match = re.search(
                    r"Выберите корректный вариант\. (.*?) нет среди допустимых значений\.",
                    color[0],
                )
                value = match.group(1) if match else None
                # value["model"] = value
                self.cleaned_data["color"] = value
                print(value)
                del self.errors["color"]

            if "transmission" in self.errors:
                transmission = self.errors["transmission"]
                match = re.search(
                    r"Выберите корректный вариант\. (.*?) нет среди допустимых значений\.",
                    transmission[0],
                )
                value = match.group(1) if match else None
                # value["model"] = value
                self.cleaned_data["transmission"] = value
                print(value)
                del self.errors["transmission"]

            valid = not bool(self.errors)
        return valid


class CarChinaFilterForm(CarFilterForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["brand"].choices = [("", "Любое")] + get_unique_param("MARKA_NAME", "china")
        
        self.fields["model"].choices = [("", "Любое")]

        self.fields["transmission"].choices = [("", "Любое")] + get_unique_param("KPP", "china")
        
        self.fields["drive"].choices = [("", "Любое")] + get_unique_param("PRIV", "china")
        
        self.fields["color"].choices = [("", "Любое")] + get_unique_param("COLOR", "china")
        
       
class CarJapanFilterForm(CarFilterForm):
    def __init__(self, *args, **kwargs):
        print("CarJapanFilterForm")
        super().__init__(*args, **kwargs)
        self.fields["brand"].choices = [("", "Любое")] + get_unique_param("MARKA_NAME", "main")
        
        self.fields["model"].choices = [("", "Любое")]

        self.fields["transmission"].choices = [("", "Любое")] + get_unique_param("KPP", "main")
        
        self.fields["drive"].choices = [("", "Любое")] + get_unique_param("PRIV", "main")
        
        self.fields["color"].choices = [("", "Любое")] + get_unique_param("COLOR", "main")


class CarKoreaFilterForm(forms.Form):
    brand = forms.ChoiceField(
        required=False,
        label="Марка",
        widget=forms.Select(
            attrs={"class": "form-control hidden-select"},
        ),
    )
    model = forms.ChoiceField(
        required=False,
        label="Модель",
        widget=forms.Select(
            attrs={"class": "form-control hidden-select"},
        ),
    )

    mileage_min = forms.Field(
        required=False,
        label="Пробег от",
        widget=forms.TextInput(
            attrs={
                "class": "form-control discharges",
                "placeholder": "Пробег от",
            },
        ),
    )
    mileage_max = forms.Field(
        required=False,
        label="до",
        widget=forms.TextInput(
            attrs={"class": "form-control discharges", "placeholder": "до"},
        ),
    )

    year_min = forms.Field(
        required=False,
        label="Год от",
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Год от"},
        ),
    )
    year_max = forms.Field(
        required=False,
        label="до",
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "до"},
        ),
    )

    engine_volume_min = forms.Field(
        required=False,
        label="Объем от",
        widget=forms.TextInput(
            attrs={
                "class": "form-control discharges",
                "placeholder": "Объем двигателя",
            },
        ),
    )
    engine_volume_max = forms.Field(
        required=False,
        label="до",
        widget=forms.TextInput(
            attrs={"class": "form-control discharges", "placeholder": "до"},
        ),
    )

    drive = forms.ModelChoiceField(
        queryset=Drive.objects.none(),
        required=False,
        label="Тип привода",
        widget=forms.Select(
            attrs={"class": "form-control hidden-select"},
        ),
    )
    color = forms.ModelChoiceField(
        queryset=Color.objects.none(),
        required=False,
        label="Цвет",
        widget=forms.Select(
            attrs={"class": "form-control hidden-select"},
        ),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["brand"].choices = [("", "Любое")] + list(
            CarKorea.objects.values_list("brand", "brand").distinct()
        )
        
        self.fields["model"].choices = [("", "Любое")] + list(
            CarKorea.objects.values_list("model", "model").distinct()
        )
        
        self.fields["drive"].queryset = Drive.objects.filter(
            carkorea__isnull=False
        ).distinct()
        
        self.fields["color"].queryset = Color.objects.filter(
            carkorea__isnull=False
        ).distinct()

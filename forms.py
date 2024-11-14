
"""forms.py"""

import pandas as pd
# import numpy as np
from .models import Commodity_Name, Crop_Production, Crop_Yield, Document_Upload, Commodity_Price
from django import forms

# commodity names
COMMODITY_NAMES = Commodity_Name.objects.all().order_by('commodity_name').values('commodity_code', 'commodity_name')

# price category
PRICE_CATEGORY = [
    ("all", "All"),
    ("retail", "Retail"),
    ("wholesale", "Wholesale"),
]

YEARS = [
    ("2019", "2019"),
    ("2020", "2020"),
    ("2021", "2021"),
    ("2022", "2022"),
]

MONTHS = [
    ("all", "All"),
    ("January", "January"),
    ("February", "February"),
    ("March", "March"),
    ("April", "April"),
    ("May", "May"),
    ("June", "June"),
    ("July", "July"),
    ("August", "August"),
    ("September", "September"),
    ("October", "October"),
    ("November", "November"),
    ("December", "December"),
]

UNITS = (
    ("kg", "kg")
)

QUANTITY = (
    (1, 1)
)

class CommodityModify(forms.Form):

    commodity_name = forms.CharField(max_length=50)
    category_type = forms.ChoiceField(choices=PRICE_CATEGORY)
    year = forms.ChoiceField(choices=YEARS)
    month = forms.ChoiceField(choices=MONTHS)
    price = forms.FloatField()
    unit = forms.ChoiceField(choices=UNITS)


class SearchPrice(forms.Form):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['commodity'] = forms.MultipleChoiceField(
            choices=[(row.commodity_code, row.commodity_name) for row in Commodity_Name.objects.all().order_by('commodity_name')],
            required=True)
        self.fields['commodity'].widget.attrs.update({'class': 'selectpicker form-control'})
        self.fields['commodity'].widget.attrs.update({'id': 'com'})

        self.fields["year"].widget.attrs["class"] = "selectpicker form-control"
        self.fields["year"].choices = [(x, y) for x, y in YEARS]

        self.fields["month"].widget.attrs["class"] = "selectpicker form-control"
        self.fields["month"].choices = [(x, y) for x, y in MONTHS]

        self.fields["price_category"].widget.attrs["class"] = "selectpicker form-control"
        self.fields["price_category"].choices = [(x, y) for x, y in PRICE_CATEGORY]

    commodity = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple)
    year = forms.MultipleChoiceField()
    month = forms.MultipleChoiceField()
    price_category = forms.MultipleChoiceField()

    class Meta:
        model = Commodity_Price


class DocumentForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(DocumentForm, self).__init__(*args, **kwargs)
        for field in iter(self.fields):
            self.fields[field].widget.attrs.update({
                'class': 'form-control'
            })

    class Meta:
        model = Document_Upload
        fields = ['document_name', 'document_type', 'document']


class ProductionByRegionSearchForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['crop'].widget.attrs.update({'class': 'selectpicker', 'id': 'crop'})
        self.fields["crop"].widget.attrs["class"] = "selectpicker form-control"

        self.fields["year"].widget.attrs["class"] = "selectpicker form-control"

        self.fields["region"].widget.attrs["class"] = "selectpicker form-control"


    # indicator = forms.ChoiceField(choices=['Cropped Area', 'Average Yield', ''])

    region = forms.ModelMultipleChoiceField(
        queryset=Crop_Production.objects.all().values_list('region', flat=True).distinct().order_by('region'),
        initial=0
    )

    crop = forms.ModelMultipleChoiceField(
        queryset=Crop_Production.objects.all().values_list('crop_type', flat=True).distinct().order_by('crop_type'),
        widget=forms.SelectMultiple,
        initial={
            "crop": [
                cat for cat in Crop_Production.objects.all().values_list("crop_type", flat=True)
            ]
        }
    )

    year = forms.ModelMultipleChoiceField(
        queryset= Crop_Production.objects.all().values_list('year', flat=True).distinct().order_by('year'),
        initial = 0
    )

class CropYieldSearchForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['crop'].widget.attrs.update({'class': 'selectpicker form-control', 'id': 'crop'})
        self.fields["crop"].widget.attrs["class"] = "selectpicker form-control"
        self.fields["year"].widget.attrs["class"] = "selectpicker form-control"
        self.fields["region"].widget.attrs["class"] = "selectpicker form-control"
        indicator = forms.ChoiceField(choices=['Cropped Area', 'Average Yield', ''])

        crop = forms.ModelMultipleChoiceField(
            queryset=Crop_Yield.objects.all().values_list('crop_type', flat=True).distinct().order_by('crop_type'),
            initial=0
        )

        region = forms.ModelMultipleChoiceField(
            queryset=Crop_Yield.objects.all().values_list('region', flat=True).distinct().order_by('region'),
            initial=0
        )

        year = forms.ModelMultipleChoiceField(
            queryset=Crop_Yield.objects.all().values_list('year', flat=True).distinct().order_by('year'),
            initial=0
)

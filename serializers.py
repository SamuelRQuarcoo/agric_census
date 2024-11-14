# imports
from rest_framework import serializers
from .models import *

# commodity prices serializer
class CommoditySerializer(serializers.ModelSerializer):
    class Meta:
        model = Commodity_Price
        fields = '__all__'
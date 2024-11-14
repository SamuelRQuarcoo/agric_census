from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Commodity_Name)
admin.site.register(Commodity_Price)
admin.site.register(Crop_Yield)
admin.site.register(Crop_Production)
admin.site.register(Document_Upload)


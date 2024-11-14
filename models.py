from django.db import models

#******************************************************************************
#                                  MODELS
#******************************************************************************

# commodity category
CATEGORY = (
    ("wholesale", "Wholesale"),
    ("wholesale", "Retail"),
)

DOCUMENT_TYPES = (
    ("production", "Production"),
    ("environment", "Environment"),
    ("trade", "Trade"),
    ("commodity_prices", "Commodity Price"),
    ("crop_projections", "Crop Projections"),
    ("research_publications", "Research & Publicatons")
)

#commodity names
class Commodity_Name(models.Model):
    main_category_code = models.CharField(max_length=4, null=False, blank=False, default='None')
    main_category_name = models.CharField(max_length=150, null=False, blank=False, default='None')
    sub_category_code = models.CharField(max_length=5, null=False, blank=False, default='None')
    sub_category_name = models.CharField(max_length=150, null=False, blank=False, default='None')
    commodity_code = models.CharField(primary_key=True, max_length=7, null=False, blank=False)
    commodity_name = models.CharField(max_length=100, null=False, blank=False, default='None')
    upload_serial_no = models.PositiveIntegerField(null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True, null=False, blank=False)
    date_updated = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.commodity_name

# commodity prices
class Commodity_Price(models.Model):
    commodity_code_year = models.CharField(primary_key=True, max_length=20, null=False, blank=False)
    commodity = models.ForeignKey(Commodity_Name, related_name='commodity',
                                  on_delete=models.CASCADE,
                                  max_length=7, null=False, blank=False)
    price_category = models.CharField(choices=CATEGORY, max_length=50, null=False, blank=False)
    year = models.PositiveIntegerField(null=False, blank=False)
    month = models.CharField(max_length=20, null=False, blank=False)
    month_year = models.CharField(max_length=20, null=True)
    price = models.FloatField(null=False, blank=False)
    unit = models.CharField(max_length=50, null=False, blank=False)
    quantity = models.CharField(max_length=10, null=False, blank=False)
    filename = models.CharField(max_length=50, null=False, blank=False)
    upload_serial_no = models.PositiveIntegerField(null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True, null=False, blank=False)
    date_updated = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.commodity

# crop yield
class Crop_Yield(models.Model):
    crop_type = models.CharField(max_length=50)
    crop_category = models.CharField(max_length=100)
    region = models.CharField(max_length=50, null=False, blank=False)
    value = models.FloatField(null=False, blank=False)
    year = models.PositiveIntegerField(null=False, blank=False)
    upload_serial_no = models.PositiveIntegerField(null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True, null=False, blank=False)
    date_updated = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.yield_crop_type + '-' + self.region

# crop production
class Crop_Production(models.Model):
    crop_type = models.CharField(max_length=50)
    crop_category = models.CharField(max_length=100)
    region = models.CharField(max_length=50, null=False, blank=False)
    value = models.FloatField(null=False, blank=False)
    year = models.PositiveIntegerField(null=False, blank=False)
    upload_serial_no = models.PositiveIntegerField(null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True, null=False, blank=False)
    date_updated = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.crop_type

# cropped area
class Cropped_Area(models.Model):
    crop_type = models.CharField(max_length=50)
    crop_category = models.CharField(max_length=100)
    region = models.CharField(max_length=50, null=False, blank=False)
    district = models.CharField(max_length=50, null=False, blank=False)
    value = models.FloatField(null=False, blank=False)
    year = models.PositiveIntegerField(null=False, blank=False)
    upload_serial_no = models.PositiveIntegerField(null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True, null=False, blank=False)
    date_updated = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.crop_type

# file/document uploads
class Document_Upload(models.Model):
    document_name = models.CharField(max_length=255, default='None')
    document_type = models.CharField(choices=DOCUMENT_TYPES, max_length=255, default='None')
    document = models.FileField(upload_to='documents/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
















































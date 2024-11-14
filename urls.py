"""url configuration file for agriStatBank application"""

from django.urls import path, include
from .views import *
from django.contrib.auth import views

app_name = "agriStatsApp"

urlpatterns = [
    path("", Index, name="index"),
    path("abouts-us/", AboutUs, name="about-us"),

    path('logout', views.LogoutView.as_view, name="logout"),
    path('login', views.LogoutView.as_view, name="login"),

    # commodity prices
    path("commodity-prices/", PriceStatisticsHome, name="commodity_prices_home"),
    path("commodity-prices-upload-preview/", CommodityPricesLoadPreview, name="commodity_prices_upload_preview"),
    path("commodity-prices-upload", CommodityPricesLoad, name="commodity_prices_upload"),
    path("commodity-prices-names_upload/", LoadCommodities, name="commodity_prices_names_upload"),
    path("commodity-prices-search/", PriceStatisticSearch, name="commodity_prices_search"),
    path("commodity-prices-modify-home/", ModifyPriceStatisticSearch, name="commodity_prices_modify_home"),
    path("commodity-prices-modify/", ModifyCommodity, name="commodity_prices"),

    # agriculture production
    path("agric-production/", ProductionHome, name="agric_production_home"),

    # crop production
    path("crop-production-search/", CropProductionSearch, name="crop_production_search"),
    path("crop-production-file_upload/", UploadProductionCreateView.as_view(), name="crop_production_file_upload"),
    path("crop-production-upload-preview/", CropProductionLoadPreview, name="crop_production_upload_preview"),
    path("crop-production-upload/", CropProductionLoad, name="crop_production_upload"),
    path("crop-production-list/", ProductionListView.as_view(), name="crop_production_list"),
    path("crop-production-download/<int:document_id>", XLSDownloadListView, name="crop_production_download_excel"),
    path("crop-production-download/<int:document_id>", PDFDownloadListView, name="crop_production_download_pdf"),
    path("crop-production-plots-stats", CropProductionPlot, name="crop_production_plots_stats"),

    # crop yield
    path("crop-yield-upload", CropYieldLoad, name="crop_yield_data_upload"),
    path("crop-yield-plots-stats", CropYieldPlot, name="crop_yield_plots_stats"),

    # cropped area
    path("cropped-area-plots-stats", CropYieldPlot, name="cropped_area_plots_stats"),

    path("crop-projections/", CropProjectionsHome, name="crop_projections_home"),
    path("environment/", EnvironmentHome, name="environment_home"),

    # trade
    path("agric-trade/", AgricTradeHome, name="agric_trade_home"),

    # research and publications
    path("research-publications/", PublicationResearchHome, name="research_publications_home"),
    path("publications/", PublicationsHome, name="publications_home"),
    path("pub-gca-reports/", GCAReports, name="pub_gca_reports"), # marked for modification
    path("gca-docs-list/", GCADocsListView.as_view(), name="gca_docs_list"),
    path("gca-docs-download/<int:document_id>", PDFDownloadListView, name="gca_docs_download"),
    path("docs-upload", UploadGCACreateView.as_view(), name="docs_upload"),

    # crop yield
    path("crop-yield-upload/", CropYieldLoad, name="crop_yield_upload"),
    path("crop-yield-search/", CropYieldSearch, name="crop_yield_search"),

    # others
    path("download-data/", DownloadData, name="download_data"),
    path("gis-maps/", CropProductionMap, name="gis_maps"),
]
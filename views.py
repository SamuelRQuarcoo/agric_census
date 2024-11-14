#****************************************************************
#* IMPORT STATEMENTS
#****************************************************************
import csv
import json

import plotly.offline
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import permission_required, login_required
from django.utils.datastructures import MultiValueDictKeyError
from django.db.utils import OperationalError, ProgrammingError, IntegrityError
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
import csv
from django.template import loader
from django.views.decorators.cache import cache_page
from rest_framework import viewsets
from django.views.generic.edit import FormView
from .models import *
from .forms import *
from .serializers import *
import io
import pandas as pd
import numpy as np
from datetime import datetime, timezone, timedelta
import calendar
import plotly.express as px
from plotly.offline import plot
import plotly.graph_objects as go
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from django.views.generic import ListView
from django.shortcuts import get_object_or_404

crop_color_map = {
        'Maize': 'olive',
        'Rice': 'magenta',
        'Millet': 'aqua',
        'Sorghum': 'yellow',
        'Cassava': 'purple',
        'Yam': 'green',
        'Cocoyam': 'bisque',
        'Plantain': 'red',
        'Groundnut': 'royalblue',
        'Cowpea': 'blue',
        'Soyabean': 'orange'
    }

color_map = {
              'Ademe/Ayoyo (jute mallow)': 'olive',
              'Alefu (Amaranthus)': 'magenta',
              'Anchovy': 'aqua',
              'Avocado Pear': 'yellow',
              'Bambara Bean': 'purple',
              'Banana (Exotic)': 'beige',
              'Banana (Local)': 'bisque',
              'Beef': 'black',
              'Cabbage': 'royalblue',
              'Carrot': 'blue',
              'Cassava': 'orange',
              'Cassava Dough': 'brown',
              'Chevon (Goat meat)': 'burlywood',
              'Chicken Meat': 'cadetblue',
              'Coconut (Fresh)': 'tomato',
              'Coconut Oil': 'chocolate',
              'Cocoyam': 'coral',
              'Corn Dough': 'cornflowerblue',
              'Cowpea (White)': 'cornsilk',
              'Dried Cassava Chips (Kokonte)': 'crimson',
              'Dried Cassava Powder (Kokonte)': 'cyan',
              'Dried Pepper (Legon 18)': 'darkblue',
              'Dried Pepper (eg. Legon 18)': 'darkcyan',
              'Fresh Cow Milk': 'darkgoldenrod',
              'Fresh Kpanla Fish': 'darkgray',
              'Fresh Pepper (Bonnet)': 'darkgrey',
              'Fresh Pepper (Legon 18)': 'darkgreen',
              'Fresh Pepper (eg. Legon 18)': 'darkkhaki',
              'Fresh Red Fish': 'darkmagenta',
              'Fresh Salmon (Mackerel) Fish': 'darkolivegreen',
              'Garden Egg': 'darkorange',
              'Gari': 'darkorchid',
              'Ginger': 'darkred',
              'Groundnut (Red)': 'darksalmon',
              'Groundnut Oil': 'darkseagreen',
              'Kako': 'darkslateblue',
              'Lettuce': 'darkslategray',
              'Maize (White)': 'darkslategrey',
              'Maize (Yellow)': 'darkturquoise',
              'Mango (Exotic)': 'darkviolet',
              'Mango (Local)': 'deeppink',
              'Melon seeds (Agushi)': 'deepskyblue',
              'Melon seeds (Agushi) Powder': 'dimgray',
              'Melon seeds (Neri)': 'dimgrey',
              'Melon seeds (Neri) Powder': 'dodgerblue',
              'Melon seeds (agushi/neri)': 'firebrick',
              'Melon seeds (agushi/neri) Powder': 'steelblue',
              'Millet': 'forestgreen',
              'Mutton (Sheep meat)': 'fuchsia',
              'Nkontomire': 'gainsboro',
              'Okro (Dried)': 'ghostwhite',
              'Okro (Fresh)': 'gold',
              'Onion': 'goldenrod',
              'Orange': 'gray',
              'Palm Fruit': 'grey',
              'Palm Oil': 'green',
              'Pawpaw': 'greenyellow',
              'Pineapple': 'honeydew',
              'Plantain (Apem)': 'hotpink',
              'Plantain (Apentu)': 'indianred',
              'Plantain (Riped)': 'indigo',
              'Pork': 'ivory',
              'Rice Imported (non perfumed)': 'khaki',
              'Rice Imported (perfumed)': 'turquoise',
              'Rice Local (non perfumed)': 'lavenderblush',
              'Rice Local (perfumed)': 'lawngreen',
              'Salted Dried Tilapia (Koobi)': 'hotpink',
              'Smoked Herring': 'lightblue',
              'Snail': 'lightcoral',
              'Sorghum': 'lightcyan',
              'Soya Bean': 'lightgoldenrodyellow',
              'Soyabean': 'lightgray',
              'Sweet Potato (ORANGE)': 'lightgrey',
              'Sweet Potato (general:white and pinkish)': 'lightgreen',
              'Tiger Nut': 'lightpink',
              'Tomato (Local)': 'lightsalmon',
              'Tomato (Navrongo)': 'lightseagreen',
              'Unshelled Groundnut': 'lightskyblue',
              'Watermelon': 'lightslategray',
              'Yam (Puna)': 'lightslategrey',
              'Yam (White)': 'lightsteelblue'
          }

#*********************************************************************
#* CREATE DATE SERIES USING MONTH AND YEAR
#*********************************************************************
def setTime(month_var, year_var):

    strDate = str(month_var) + '-' + str(int(year_var))
    f_date = datetime.strptime(strDate, '%B-%Y')
    f_date = f_date.strftime('%b %Y')

    return f_date

#*********************************************************************
#* HOME PAGE
#*********************************************************************
def Index(request):
    """View function for home page of site."""

    #get number of hours since last update
    price_stats_update = Commodity_Price.objects.all()

    if len(price_stats_update) > 0:

        df_price_stats_update = pd.DataFrame(price_stats_update.values())
        df_price_stats_update = df_price_stats_update[['date_created', 'date_updated']]
        max_date = df_price_stats_update['date_created'].max()
        last_update_date = (datetime.now(timezone.utc) - max_date) / np.timedelta64(1, 'm')
        last_update_date = str(last_update_date)[:2]

        #print(last_update_date)
        context = {
            "minutes_updated": last_update_date
        }
        template = "index.html"

        return render(request, template, context)

    template = "index.html"
    return render(request, template)

#*********************************************************************
#* ABOUT US
#*********************************************************************
def AboutUs(request):

    template = "about_us.html"
    return render(request, template)

#*********************************************************************
#* PRICE STATISTICS HOME
#*********************************************************************
def PriceStatisticsHome(request):
    """View function for commodity prices home page"""

    wholesale_2019_by_main_cat_BAR = None

    #*************************************************************
    # Mean Price Changes, Wholesale & Retail, Dumb Bell Plot
    #*************************************************************

    queryset_2019_retail = Commodity_Price.objects.filter(year='2019', price_category='retail')
    queryset_2019_wholesale = Commodity_Price.objects.filter(year='2019', price_category='wholesale')
    df_2019_retail = pd.DataFrame(queryset_2019_retail.values())
    df_2019_wholesale = pd.DataFrame(queryset_2019_wholesale.values())

    # queryset_2020_wholesale = Commodity_Prices.objects.filter(year='2020', price_category='wholesale')
    # df_2020_retail = pd.DataFrame(queryset_2020_retail.values())
    # df_2020_wholesale = pd.DataFrame(queryset_2020_wholesale.values())

    queryset_commodities = Commodity_Name.objects.all()
    df_commodities = pd.DataFrame(queryset_commodities.values())

    mean_price_changes_2019_Dumbell = None
    retail_2019_by_main_cat_BAR = None
    retail_2019_by_sub_cat_TREEMAP = None
    wholesale_2019_by_main_cat_BAR = None
    retail_2019_by_sub_cat_BAR_1 = None
    wholesale_2019_by_sub_cat_BAR_1 = None
    top_10_most_expensive_retail_2019 = None
    top_10_least_expensive_retail_2019 = None
    wholesale_2019_by_sub_cat_TREEMAP = None

    if len(df_2019_retail) > 0:
        if len(df_2019_wholesale) > 0: # data for both wholesale and retail

            # merge price and commodity data
            merged_2019_retail = pd.merge(df_2019_retail, df_commodities, left_on='commodity_id', right_on="commodity_code", how="inner")
            merged_2019_wholesale = pd.merge(df_2019_wholesale, df_commodities, left_on='commodity_id', right_on="commodity_code", how="inner")

            months = [
                'January',
                'February',
                'March',
                'April',
                'May',
                'June',
                'July',
                'August',
                'September',
                'October',
                'November',
                'December'
            ]

        #     #merged_2019_df
            final_df = pd.concat([merged_2019_retail, merged_2019_wholesale], axis=0)

            # final_df = merged_2019_retail
            commodities_2019_retail = set([i for i in merged_2019_retail['commodity_name']])
            commodities_2019_wholesale = set([i for i in merged_2019_wholesale['commodity_name']])
            all_commodities = set.intersection(commodities_2019_retail, commodities_2019_wholesale)
            final_df = final_df[final_df['commodity_name'].isin(all_commodities)]

            commodities = (
                final_df.sort_values(by=['price'])['commodity_name'].unique()
            )

            data_1 = {'line_x': [], 'line_y': [], 'retail': [], 'wholesale': []}

            for commodity in commodities:
                data_1['retail'].extend([final_df.loc[(final_df['price_category'] == 'retail') & (final_df['commodity_name'] == commodity)][
                                           'price'].values.mean()])
                data_1['wholesale'].extend([final_df.loc[(final_df['price_category'] == 'wholesale') & (final_df['commodity_name'] == commodity)][
                                           'price'].values.mean()])
                data_1["line_x"].extend(
                    [
                        final_df.loc[(final_df['price_category'] == 'retail') & (final_df['commodity_name'] == commodity)][
                            'price'].values.mean(),
                        final_df.loc[(final_df['price_category'] == 'wholesale') & (final_df['commodity_name'] == commodity)][
                            'price'].values.mean(),
                        None,
                    ]
                )
                data_1["line_y"].extend([commodity, commodity, None]),

            fig1 = go.Figure(
                data=[
                    go.Scatter(
                        x=data_1["line_x"],
                        y=data_1["line_y"],
                        mode="lines",
                        showlegend=False,
                        marker=dict(color="green", size=10)
                    ),
                    go.Scatter(
                        x=data_1["retail"],
                        y=commodities,
                        mode="markers",
                        name="Retail",
                        marker=dict(
                            color="green",
                            size=10
                        )
                    ),
                    go.Scatter(
                        x=data_1["wholesale"],
                        y=commodities,
                        mode="markers",
                        name="Wholesale",
                        marker=dict(
                            color="blue",
                            size=10
                        )
                    ),
                ]
            )

            fig1.update_layout(
                title="Mean Price Differences between Wholesale and Retail (2019)",
                height=1200,
                width=1100,
                legend_itemclick=False
            )

            mean_price_changes_2019_Dumbell = plot(fig1, output_type="div",
                                                       config={"displayModeBar": True,
                                                            "displaylogo": False,
                                                            'modeBarButtonsToRemove': [
                                                                'zoom2d',
                                                                'toggleSpikelines',
                                                                'pan2d',
                                                                'select2d',
                                                                'lasso2d',
                                                                'autoScale2d',
                                                                'hoverClosestCartesian',
                                                                'hoverCompareCartesian',
                                                                'resetScale2d'
                                                            ]
                                                       }
                                                   )
        else:
            # data for only retail
            merged_2019_retail = pd.merge(df_2019_retail, df_commodities, left_on='commodity_id',
                                          right_on="commodity_code", how="inner")

            months = [
                'January',
                'February',
                'March',
                'April',
                'May',
                'June',
                'July',
                'August',
                'September',
                'October',
                'November',
                'December'
            ]

            #     #merged_2019_df
            final_df = merged_2019_retail

            # final_df = merged_2019_retail
            commodities_2019_retail = set([i for i in merged_2019_retail['commodity_name']])
            all_commodities = commodities_2019_retail
            final_df = final_df[final_df['commodity_name'].isin(all_commodities)]

            commodities = (
                final_df.sort_values(by=['price'])['commodity_name'].unique()
            )

            data_1 = {'line_x': [], 'line_y': [], 'retail': [], 'wholesale': []}

            for commodity in commodities:
                data_1['retail'].extend(
                    [final_df.loc[(final_df['price_category'] == 'retail') & (final_df['commodity_name'] == commodity)][
                         'price'].values.mean()])
                data_1['wholesale'].extend([final_df.loc[(final_df['price_category'] == 'wholesale') & (
                            final_df['commodity_name'] == commodity)][
                                                'price'].values.mean()])
                data_1["line_x"].extend(
                    [
                        final_df.loc[
                            (final_df['price_category'] == 'retail') & (final_df['commodity_name'] == commodity)][
                            'price'].values.mean(),
                        final_df.loc[
                            (final_df['price_category'] == 'wholesale') & (final_df['commodity_name'] == commodity)][
                            'price'].values.mean(),
                        None,
                    ]
                )
                data_1["line_y"].extend([commodity, commodity, None]),

            fig1 = go.Figure(
                data=[
                    go.Scatter(
                        x=data_1["line_x"],
                        y=data_1["line_y"],
                        mode="lines",
                        showlegend=False,
                        marker=dict(color="green", size=10)
                    ),
                    go.Scatter(
                        x=data_1["retail"],
                        y=commodities,
                        mode="markers",
                        name="Retail",
                        marker=dict(
                            color="green",
                            size=10
                        )
                    ),
                    go.Scatter(
                        x=data_1["wholesale"],
                        y=commodities,
                        mode="markers",
                        name="Wholesale",
                        marker=dict(
                            color="blue",
                            size=10
                        )
                    ),
                ]
            )

            fig1.update_layout(
                title="Mean Price Changes for Wholesale and Retail (2019)",
                height=1200,
                width=1200,
                legend_itemclick=False
            )

            mean_price_changes_2019_Dumbell = plot(fig1,
                                                   output_type="div",
                                                   config={"displayModeBar": True,
                                                           "displaylogo": False,
                                                           'modeBarButtonsToRemove': [
                                                               'zoom2d',
                                                               'toggleSpikelines',
                                                               'pan2d',
                                                               'select2d',
                                                               'lasso2d',
                                                               'autoScale2d',
                                                               'hoverClosestCartesian',
                                                               'hoverCompareCartesian',
                                                               'resetScale2d'
                                                            ]}
                                                   )


        # *************************************************
        # Mean Prices (Retail, 2019) by Main Category (Bar)
        #**************************************************
        merged_2019_retail = pd.merge(merged_2019_retail, df_commodities, left_on='commodity_id',
                                         right_on="commodity_code", how="inner")
        #print(merged_2019_retail.columns)
        merged_2019_retail_by_main_cat = merged_2019_retail.groupby(['main_category_code_x', 'main_category_name_x'])[
            'price'].mean()
        merged_2019_retail_by_main_cat = merged_2019_retail_by_main_cat.reset_index().sort_values(by='price')
        merged_2019_retail_by_main_cat['prices'] = ['{:.2f}'.format(x) for x in
                                                       merged_2019_retail_by_main_cat['price']]

        fig2 = px.bar(merged_2019_retail_by_main_cat,
                      x='main_category_name_x',
                      y='prices',
                      color='main_category_name_x',
                      text_auto='.2s',
                      title="Mean Prices (Retail, 2019) of Commodities by Category",
                      labels={'main_category_name_x': 'Main Category', 'prices': 'Price'}
                      )

        fig2.update_layout(margin=dict(t=50, l=25, r=25, b=25))
        fig2.update_yaxes(ticks="outside", tickwidth=2, tickcolor='crimson', ticklen=10, col=1)
        fig2.update(layout_yaxis_range = [0,10])

        retail_2019_by_main_cat_BAR = plot(fig2,
                                           output_type="div",
                                           config={"displayModeBar": True,
                                                   "displaylogo": False,
                                                   'modeBarButtonsToRemove': [
                                                       'zoom2d',
                                                       'toggleSpikelines',
                                                       'pan2d',
                                                       'select2d',
                                                       'lasso2d',
                                                       'autoScale2d',
                                                       'hoverClosestCartesian',
                                                       'hoverCompareCartesian',
                                                       'resetScale2d'
                                                   ]}
                                           )


        # *****************************************************
        # Mean Prices (Retail, 2019) by Main Category (Treemap)
        #******************************************************
        merged_2019_retail_by_main_cat = merged_2019_retail.groupby(['main_category_code_x',
                                                                     'main_category_name_x',
                                                                     'sub_category_name_x'])['price'].mean().reset_index()
        merged_2019_retail_by_main_cat['prices'] = ['{:.2f}'.format(x) for x in
                                                       merged_2019_retail_by_main_cat['price']]
        merged_2019_retail_by_main_cat['prices'] = merged_2019_retail_by_main_cat['prices'].astype('float')

        fig_2_0 = px.treemap(merged_2019_retail_by_main_cat,
                             path=["main_category_name_x", "sub_category_name_x"],
                             values="prices",
                             color="sub_category_name_x",
                             # hover_data = ["iso_alpha"],
                             color_continuous_scale="RdBu",
                             color_continuous_midpoint=np.average(merged_2019_retail_by_main_cat["prices"],
                                                                  weights=merged_2019_retail_by_main_cat["prices"]),
                             title="Distribution of Prices (Retail, 2019) of Commodities"
                             )
        fig_2_0.update_layout(margin=dict(t=50, l=25, r=25, b=25))

        retail_2019_by_sub_cat_TREEMAP = plot(fig_2_0,
                                            output_type="div",
                                            config={"displayModeBar": True,
                                                    "displaylogo": False,
                                                    'modeBarButtonsToRemove': [
                                                        'zoom2d',
                                                        'toggleSpikelines',
                                                        'pan2d',
                                                        'select2d',
                                                        'lasso2d',
                                                        'autoScale2d',
                                                        'hoverClosestCartesian',
                                                        'hoverCompareCartesian',
                                                        'resetScale2d'
                                                    ]},
                                            )

        #*******************************************
        # Mean Prices (Retail, 2019) by Sub-Category
        #*******************************************
        # merged_2019_retail_by_main_sub_cat = merged_2019_retail.groupby(['main_category_name', 'sub_category_name']).mean(
        #     'prices')
        # merged_2019_retail_by_main_sub_cat = merged_2019_retail_by_main_sub_cat.reset_index()
        # merged_2019_retail_by_main_sub_cat = merged_2019_retail_by_main_sub_cat.astype({'year': int})
        # merged_2019_retail_by_main_sub_cat['prices'] = ['{:.2f}'.format(x) for x in merged_2019_retail_by_main_sub_cat['price']]
        #
        # fig2_1 =  px.bar(merged_2019_retail_by_main_sub_cat, x="main_category_name",
        #                  y="price", color="sub_category_name", text="sub_category_name",
        #                  title="Mean Prices (Retail, 2019) of Commodities by Sub COICOP Category")
        # fig2_1.update_traces(textfont_size=14, textangle=0, textposition="outside", cliponaxis=False)
        # # fig2_1.update_xaxes(tickangle=90)
        #
        # retail_2019_by_sub_cat_BAR_1 = plot(fig2_1,
        #                                     output_type="div",
        #                                     config={"displayModeBar": True,
        #                                             "displaylogo": False,
        #                                             'modeBarButtonsToRemove': [
        #                                                 'zoom2d',
        #                                                 'toggleSpikelines',
        #                                                 'pan2d',
        #                                                 'select2d',
        #                                                 'lasso2d',
        #                                                 'autoScale2d',
        #                                                 'hoverClosestCartesian',
        #                                                 'hoverCompareCartesian',
        #                                                 'resetScale2d'
        #                                             ]}
        #                                     )


        # *****************************************
        # Mean Prices (Wholesale, 2019) by Category
        # *****************************************
        if len(df_2019_wholesale) and len(df_commodities) > 0:
            merged_2019_wholesale = pd.merge(df_2019_wholesale, df_commodities, left_on='commodity_id',
                                             right_on="commodity_code", how="inner")

            merged_2019_wholesale_by_main_cat = merged_2019_wholesale.groupby(['main_category_code', 'main_category_name'])['price'].mean()
            merged_2019_wholesale_by_main_cat = merged_2019_wholesale_by_main_cat.reset_index().sort_values(by='price')
            #merged_2019_wholesale_by_main_cat = merged_2019_wholesale_by_main_cat.astype({'year': int})
            merged_2019_wholesale_by_main_cat['prices'] = ['{:.2f}'.format(x) for x in merged_2019_wholesale_by_main_cat['price']]
            #print(merged_2019_wholesale_by_main_cat)

            fig3 = px.bar(merged_2019_wholesale_by_main_cat,
                          x='main_category_name',
                          y='price',
                          color='main_category_name',
                          text_auto='.2s',
                          title="Mean Prices (Wholesale, 2019) of Commodities by Category",
                          labels={'main_category_name': 'Main Category', 'price': 'Price'}
                          )
            fig3.update_yaxes(ticks="outside", tickwidth=2, tickcolor='crimson', ticklen=10, col=1)
            wholesale_2019_by_main_cat_BAR = plot(fig3,
                                                  output_type="div",
                                                  config={"displayModeBar": True,
                                                          "displaylogo": False,
                                                          'modeBarButtonsToRemove': [
                                                              'zoom2d',
                                                              'toggleSpikelines',
                                                              'pan2d',
                                                              'select2d',
                                                              'lasso2d',
                                                              'autoScale2d',
                                                              'hoverClosestCartesian',
                                                              'hoverCompareCartesian',
                                                              'resetScale2d'
                                                          ]}
                                                  )

            # ******************************************************
            # Prices Distribution (Wholesale, 2019) by Sub-Category
            # ******************************************************
            if len(merged_2019_wholesale) > 0:
                merged_2019_wholesale_by_main_cat = merged_2019_wholesale.groupby(['main_category_code',
                                                                             'main_category_name',
                                                                             'sub_category_name'])[
                    'price'].mean().reset_index()
                merged_2019_wholesale_by_main_cat['prices'] = ['{:.2f}'.format(x) for x in
                                                            merged_2019_wholesale_by_main_cat['price']]
                merged_2019_wholesale_by_main_cat['prices'] = merged_2019_wholesale_by_main_cat['prices'].astype('float')

                fig3_1 = px.treemap(merged_2019_wholesale_by_main_cat,
                                    path=["main_category_name", "sub_category_name"],
                                    values="prices",
                                    color="sub_category_name",
                                    # hover_data = ["iso_alpha"],
                                    color_continuous_scale="RdBu",
                                    color_continuous_midpoint=np.average(merged_2019_retail_by_main_cat["prices"],
                                                                         weights=merged_2019_retail_by_main_cat[
                                                                             "prices"]),
                                    title="Price Distribution (Wholesale, 2019) of Commodities"
                                    )
                fig3_1.update_layout(margin=dict(t=50, l=25, r=25, b=25))

                wholesale_2019_by_sub_cat_TREEMAP = plot(fig3_1,
                                                    output_type="div",
                                                    config={"displayModeBar": True,
                                                            "displaylogo": False,
                                                            'modeBarButtonsToRemove': [
                                                                'zoom2d',
                                                                'toggleSpikelines',
                                                                'pan2d',
                                                                'select2d',
                                                                'lasso2d',
                                                                'autoScale2d',
                                                                'hoverClosestCartesian',
                                                                'hoverCompareCartesian',
                                                                'resetScale2d'
                                                            ]}
                                                )


        # ***************************************************************
        # Top 10 Most Expensive Commodities (Mean Prices, Retail 2019)
        # ***************************************************************
        #
        if len(df_2019_retail) and len(df_commodities) > 0:
            merged_2019_retail_grp_df = merged_2019_retail.groupby(['commodity_name_x'])['price'].mean().reset_index()
            df_10_most_expensive = merged_2019_retail_grp_df.sort_values(by=['price'], ascending=False)[:5]
            #df_10_most_expensive['price'] = ['{:.2f}'.format(x) for x in df_10_most_expensive['price']]

            print(df_10_most_expensive)
            fig2_2 = px.bar(df_10_most_expensive,
                            x = 'commodity_name_x',
                            y="price",
                            color="commodity_name_x",
                            hover_name="commodity_name_x",
                            title="Top 5 Most Expensive Commodities -  Retail, 2019",
                            labels={'price': 'Price', 'commodity_name_x': 'Commodity'},
                            color_discrete_map = color_map
                            )
            #fig2_2.update_layout(yaxis_range=[0, 40])
            fig2_2.update_xaxes(type='category')
            #fig2_2.update_yaxes(ticks="outside", tickwidth=1, tickcolor='crimson', ticklen=10, col=1)

            top_10_most_expensive_retail_2019 = plot(fig2_2,
                                                     output_type="div",
                                                     config={"displayModeBar": True,
                                                             "displaylogo": False,
                                                             'modeBarButtonsToRemove': [
                                                                 'zoom2d',
                                                                 'toggleSpikelines',
                                                                 'pan2d',
                                                                 'select2d',
                                                                 'lasso2d',
                                                                 'autoScale2d',
                                                                 'hoverClosestCartesian',
                                                                 'hoverCompareCartesian',
                                                                 'resetScale2d'
                                                             ]}
                                                     )


        # ***************************************************************
        # Top 10 Least Expensive Commodities (Mean Prices, Retail 2019)
        # ***************************************************************
        #
        if len(df_2019_retail) and len(df_commodities) > 0:
            merged_2019_retail_grp_df = merged_2019_retail.groupby(['commodity_name_x'])[
                'price'].mean().reset_index()
            df_10_most_expensive = merged_2019_retail_grp_df.sort_values(by=['price'], ascending=True)[:5]
            # df_10_most_expensive['price'] = ['{:.2f}'.format(x) for x in
            #                                  df_10_most_expensive['price']]
            fig2_3 = px.bar(df_10_most_expensive,
                            x='commodity_name_x',
                            y="price",
                            color="commodity_name_x",
                            hover_name="commodity_name_x",
                            title="Top 5 Least Expensive Commodities -  Retail, 2019",
                            labels={'price': 'Price', 'commodity_name_x': 'Commodity'},
                            color_discrete_map=color_map
                            )

            fig2_3.update_layout(margin=dict(t=50, l=25, r=25, b=25))
            fig2_3.update_yaxes(ticks="outside", tickwidth=2, tickcolor='crimson', ticklen=10, col=1)
            fig2_3.update(layout_yaxis_range=[0, 5])
            fig2_3.update_xaxes(type='category')

            top_10_least_expensive_retail_2019 = plot(fig2_3,
                                                      output_type="div",
                                                      config={"displayModeBar": True,
                                                              "displaylogo": False,
                                                              'modeBarButtonsToRemove': [
                                                                  'zoom2d',
                                                                  'toggleSpikelines',
                                                                  'pan2d',
                                                                  'select2d',
                                                                  'lasso2d',
                                                                  'autoScale2d',
                                                                  'hoverClosestCartesian',
                                                                  'hoverCompareCartesian',
                                                                  'resetScale2d'
                                                              ]}
                                                      )


        context = {
            "Plot_Mean_Price_Change": mean_price_changes_2019_Dumbell,
            "Plot_Retail_2019_By_Category": retail_2019_by_main_cat_BAR,
            "Plot_Retail_2019_By_Category_Hierachy": retail_2019_by_sub_cat_TREEMAP,
            "Plot_Wholesale_2019_By_Category": wholesale_2019_by_main_cat_BAR,
            "Plot_Wholesale_2019_By_Category_Hierachy": wholesale_2019_by_sub_cat_TREEMAP,
            # "Plot_Wholesale_2019_By_Sub_Category": wholesale_2019_by_sub_cat_BAR_1,
            "Plot_Top_10_Most_Expensive_Retail_2019": top_10_most_expensive_retail_2019,
            "Plot_Top_10_Least_Expensive_Retail_2019": top_10_least_expensive_retail_2019,
        }

        return render(request, "commodity_prices_home.html", context)

    return render(request, "commodity_prices_home.html")

#*********************************************************************
#* PERFORM FILE TYPE CHECKS ON UPLOADED DATA FILE
#**********************************************************************

# file type check
def file_extension_check(filename):

    # name check
    if filename != None:

        # commodity_prices
        # status report
        status = {}

        # validate type of file uploaded
        file_type = ''.join(filename.split('.')[1:])  # extract type
        if file_type != 'csv':
            status['filename'] = 'fail'
            status['description'] = "Required file extension is " + str('CSV').upper() + ". Current file is " + file_type.upper()
        else:
            status['filename'] = 'success'

        # final results
        results_dic = {'file': filename, 'status': status}

        return results_dic


# file type check
def file_type_check(filename, module_name):

    # name check
    if filename != None:

        # commodity_prices
        if module_name == 'commodity_prices':

            # status report
            status = {}

            # validate type of file uploaded
            file_type = '_'.join(filename.split('_')[:2]) # extract type
            if file_type != 'commodity_prices':
                status['filename'] = 'fail'
                status['description'] = "Expected file type is " + module_name.upper() + ". Current file is " + file_type.upper()
            else:
                status['filename'] = 'success'

            # final results
            results_dic = {'file': filename, 'status': status}

            return results_dic

        # production
        if module_name == 'crop_production':

            # status report
            status = {}

            # validate type of file uploaded
            file_type = '_'.join(filename.split('_')[:2]) # extract type
            if file_type != 'crop_production':
                status['filename'] = 'fail'
                status['description'] = "Expected file type is " + module_name.upper() + ". Current file is " + file_type.upper()
            else:
                status['filename'] = 'success'

            # final results
            results_dic = {'file': filename, 'status': status}

            return results_dic


#*********************************************************************
#* PERFORM STRUCTURAL CHECKS ON UPLOADED DATA FILE
#**********************************************************************

# data columns check
def data_column_check(df, module_name):

    file_struct = []

    try:

        # columns check
        if module_name == "commodity_prices":
            file_struct = [
                # 'Commodity_Code',
                'Commodity_Name',
                'January', 'February', 'March','April', 'May', 'June',
                'July','August', 'September', 'October', 'November',
                'Price_Category', 'Year', 'Unit','Quantity'
            ]
        elif module_name == "commodity_names":
            file_struct = [
                "main_category_code",
                "main_category_code",
                "sub_category_code",
                "sub_category_name",
                "commodity_code",
                "commodity_name"
            ]

        elif module_name in ["crop_yield", "crop_production"]:
            file_struct = [
                "Region",
                "Maize", "Rice", "Millet", "Sorghum", "Cassava", "Yam",
                "Cocoyam", "Plantain", "Groundnut", "Cowpea", "Soyabean",
                "Year", "Crop_Category"
            ]

        data_frame_cols = [x.strip() for x in df.columns]
        # print(data_frame_cols)

        status = {}
        for field in file_struct:
            if field in data_frame_cols:
                status[field] = 'pass'
            else:
                status[field] = 'fail'

        # final results
        results_dic = {'file': df, 'status': status}

        return results_dic

    except ProgrammingError as error:

        status['STATUS_REPORT'] = "Nan values in dataset"

        # final results
        results_dic = {'file': df, 'status': status}

        return results_dic

    except ProgrammingError as error:

        status['STATUS_REPORT'] = "Nan values in dataset"

        # final results
        results_dic = {'file': df, 'status': status}

        return results_dic

    except ObjectDoesNotExist:

        status['STATUS_REPORT'] = "Commodity does NOT exist!"

        # final results
        results_dic = {'file': df, 'status': status}
        return  results_dic


#**********************************************************************
#* PERFORM DUPLICATES CHECKS ON DATA FILE
#**********************************************************************
def data_duplicate_checks(df, type_of_file):

    results_dic = {}

    try:
        if type_of_file == "commodity_names":

            all_codes = [x for x in df['commodity_code']]

            dups = {}
            for c in all_codes:
                if c in dups.keys():
                    dups[c] = dups[c] + 1
                else:
                    dups[c] = 1

            sorted(dups.items())

            status = {}
            for k, v in dups.items():
                if v > 1:
                    status[k] = 'DUPLICATE'
                else:
                    status[k] = 'pass'

            results_dic = {'file': df, 'status': status}

        return results_dic
    except IntegrityError as error:

        status['STATUS_REPORT'] = "Data Duplication Error!"
        results_dic = {'file': df, 'status': status}

        return results_dic

#**********************************************************************
#  LOAD COMMODITY PRICES
#**********************************************************************
@login_required
def CommodityPricesLoadPreview(request):
    """Preview upload commodity prices"""

    #load form based on request type
    if request.method == "POST":

        # error status report dictionary
        status = {}

        # get the csv file
        file = request.FILES["file"]

        # *** CHECK #1 run file extension #1 ***
        results = file_extension_check(file.name)
        file_extension_report = results['status']

        for f, s in file_extension_report.items():
            if s == "fail":
                file_extension_report['STATUS_REPORT'] = "File extension checks failed:"
                messages.error(request, file_extension_report)
                return redirect("agriStatsApp:commodity_prices_upload_preview")

        # *** CHECK #2 run file type checks ***
        results = file_type_check(file.name, "commodity_prices")
        file_type_check_report = results['status']

        for f, s in file_type_check_report.items():
            if s == "fail":
                file_type_check_report['STATUS_REPORT'] = "File type checks failed:"
                messages.error(request, file_type_check_report)
                return redirect("agriStatsApp:commodity_prices_upload_preview")

        uploadedfile = file.name
        df = pd.read_csv(file)      # read uploaded file

        # *** CHECK #3 run data column checks ***
        results = data_column_check(df, "commodity_prices")
        data_column_check_report = results['status']

        for f, s in data_column_check_report.items():
            if s == "fail":
                data_column_check_report['STATUS_REPORT'] = "Data columns checks failed:"
                messages.error(request, data_column_check_report)
                return redirect("agriStatsApp:commodity_prices_upload_preview")

        months = [
            'January', 'February', 'March', 'April', 'May', 'June',
            'July', 'August', 'September', 'October', 'November', 'December'
        ]

        # unpivot dataframe
        df = pd.melt(df,
                     id_vars=["Commodity_Name", "Price_Category", "Year", "Unit", "Quantity"],
                     value_vars=months,
                     var_name="Month",
                     value_name="Price"
                     )

        df_html = df.to_html(table_id="test", classes=["table-bordered", "table-striped", "table-hover", "display nowrap"])

        request.session['data_frame'] = df.to_dict('records')
        request.session['filename'] = file.name
        request.session['total_rows'] = len(df)

        template = "commodity_prices_upload_preview.html"  # set template name
        context = {
            'uploadedfilename': uploadedfile,
            'data_html': df_html
        }

        return render(request, template, context)
    else:
        template = "commodity_prices_upload_preview.html"  # set template name

        return render(request, template)

#**********************************************************************
#  PREVIEW COMMODITY PRICES LOAD DATA
#**********************************************************************
@login_required
def CommodityPricesLoad(request):
    """Upload of commodities"""

    template = "commodity_prices_upload.html"
    status = {}

    if request.method == 'GET':
        data_frame_dic = request.session.get('data_frame')
        df = pd.DataFrame(data_frame_dic)

        filename = request.session.get('filename')
        type_of_file = 'Commodity Prices'

        total_rows = request.session.get('total_rows')
        upload_date = datetime.now()

        context = {
            'filename': filename,
            'type_of_file': type_of_file,
            'total_rows': total_rows,
            'upload_date': upload_date
        }

        return render(request, template, context)
    else:
        # POST method - uppload data

        data_frame_dic = request.session.get('data_frame')
        df = pd.DataFrame(data_frame_dic)

        # pivot the data
        try:

            # add commodity codes to the dataframe
            queryset_commodities = Commodity_Name.objects.all()
            if len(queryset_commodities) == 0:
                status['STATUS_REPORT'] = "Commoddity names not loaded!"
                messages.add_message(request, messages.ERROR, status)

                return redirect("agriStatsApp:commodity_prices_upload")

            df_commodities = pd.DataFrame(queryset_commodities.values())

            df_merge = pd.merge(df, df_commodities, left_on='Commodity_Name', right_on="commodity_name",
                                   how="left")

            # transform month field to a time series
            # verified_df_2['Year'] = verified_df_2['Year'].fillna(0).astype('int')
            df_merge['Month_Year'] = list(
                map(setTime, df_merge['Month'], df_merge['Year'].fillna(-1).astype('int')))

            # save data
            commodities_error = []
            # verified_df_2.index
            # print(verified_df_2[50:100])
            for i in df_merge.index:
                code = Commodity_Name.objects.values_list('commodity_code').get(
                    commodity_name=df_merge["Commodity_Name"][i])
                commodity_name_check = df_merge["Commodity_Name"][i]

                # commodity_code = str(code[0])
                # year_active = str(verified_df_2["Year"][i])

                created = Commodity_Price.objects.update_or_create(
                    commodity_code_year=str(code[0]) + '_' +
                                        str(df_merge["Year"][i]) + '_' +
                                        str(df_merge["Month"][i])[:3] + '_' +
                                        str(df_merge["Price_Category"][i])[:3],
                    commodity_id=code[0],
                    price_category=df_merge["Price_Category"][i],
                    year=df_merge["Year"][i],
                    unit=df_merge["Unit"][i],
                    quantity=df_merge["Quantity"][i],
                    month=df_merge["Month"][i],
                    month_year=df_merge["Month_Year"][i],
                    price=df_merge["Price"][i],
                    date_created=datetime.now()
                )
                # print(created)

        except KeyError as error:
            status['STATUS_REPORT'] = "Data Duplication Error! -" + str(error)
            messages.add_message(request, messages.ERROR, status)

            return redirect("agriStatsApp:commodity_prices_upload")

        except IntegrityError as error:
            status['STATUS_REPORT'] = "Data duplication error! Process aborted"
            messages.add_message(request, messages.ERROR, status)

            return redirect("agriStatsApp:commodity_prices_upload")

        except ProgrammingError as errorimport:
            status['STATUS_REPORT'] = "Nan values in dataset"
            messages.add_message(request, messages.ERROR, status)

            return redirect("agriStatsApp:commodity_prices_upload")

        except ObjectDoesNotExist:
            status['STATUS_REPORT'] = "Commodity does NOT exist! - " + str(commodity_name_check)
            messages.add_message(request, messages.ERROR, status)

            return redirect("agriStatsApp:commodity_prices_upload")

        except MultiValueDictKeyError:
            messages.error(request, "No file selected or invalid file")
            return redirect("agriStatsApp:commodity_prices_upload")
        except OperationalError:
            messages.error(request, "The database is locked or table is not available!")
            return redirect("agriStatsApp:commodity_prices_upload")

        else:
            messages.success(request, "All data rows in csv file uploaded successfully!")

            return redirect("agriStatsApp:commodity_prices_upload")

#**********************************************************************
#* LOAD COMMODITIES
#**********************************************************************
@login_required
def LoadCommodities(request):
    """Load commodity items"""

    try:
        template = "commodity_prices_names_upload.html"    #set template name

        #load form based on request type
        if request.method == "GET":
            return render(request, template)

        #get the csv file
        csv_file = request.FILES["file"]

        # validate type of file uploaded
        if not csv_file.name.endswith(".csv") or csv_file == None:
            messages.error(request, "This is not a csv file")

            return redirect("agriStatsApp:commodity_prices_names_upload")

        # read uploaded file
        df = pd.read_csv(csv_file)

        # run structure checks
        results = file_type_check(df, "commodity_names")
        verified_df = results['file']
        status = results['status']

        for f, s in status.items():
            if s == "fail":
                status['STATUS_REPORT'] = "Structure checks FAILED!:"
                messages.error(request, status)
                return redirect("agriStatsApp:commodity_prices_names_upload")


        # run data duplicate checks
        results = data_duplicate_checks(df, "commodity_names")
        verified_df = results['file']
        status = results['status']

        for f, s in status.items():
            if s == "DUPLICATE":
                status['STATUS_REPORT'] = "Duplicate checks FAILED!:"
                messages.error(request, status)
                return redirect("agriStatsApp:commodity_prices_names_upload")

        # save data
        # print(verified_df.columns)
        for i in range(len(verified_df)):
            created = Commodity_Name.objects.update_or_create(
                main_category_code=verified_df["main_category_code"][i],
                main_category_name=verified_df["main_category_name"][i],
                sub_category_code=verified_df["sub_category_code"][i],
                sub_category_name = verified_df["sub_category_name"][i],
                commodity_code=verified_df["commodity_code"][i],
                commodity_name=verified_df["commodity_name"][i],
                date_created = datetime.now(),
                date_updated=datetime.now()
            )

        context = {}

        messages.success(request, "All data rows in csv file uploaded successfully!")
        return redirect("agriStatsApp:commodity_prices_names_upload")

    except MultiValueDictKeyError:
        messages.error(request, "No file selected or invalid file")
        return redirect("agriStatsApp:commodity_prices_names_upload")
    except OperationalError:
        messages.error(request, "The database is locked or table is not available!")
        return redirect("agriStatsApp:commodity_prices_names_upload")
    except IntegrityError:
        messages.error(request, "Data already exist. Attempt to duplicate data in database. Data integrity checks failed!")
        return redirect("agriStatsApp:commodity_prices_names_upload")
    else:
        context = {}

        render(request, template, context)

#**********************************
#* AGRIC PRODUCTION HOME
#**********************************
def ProductionHome(request):
    """View function for Agricultural Production home page"""

    template = "agric_value_chain_home.html"
    return render(request, template)

#**********************************
#* ENVIRONMENT HOME
#**********************************
def EnvironmentHome(request):
    """View function for Environment home page"""

    template = "environment_home.html"
    return render(request, template)

#**********************************
#* AGRIC TRADE HOME
#**********************************
def AgricTradeHome(request):
    """View function for Agric Trade home page"""

    template = "agric_trade_home.html"
    return render(request, template)

def PublicationResearchHome(request):
    """View function for ResearchPublications home page"""

    template = "publication_research_home.html"
    return render(request, template)

def PublicationsHome(request):
    """View function for Publications home page"""

    template = "publications_home.html"
    return render(request, template)

def GCAReports(request):
    """View function for GCA Reports"""

    template = "pub_gca_reports.html"
    return render(request, template)

def CropProjectionsHome(request):
    """View function for Environment home page"""

    template = "crop_projections_home.html"
    return render(request, template)

#**********************************************************************
#* LOAD CROP YIELD
#**********************************************************************
@login_required
def CropYieldLoad(request):
    """Load crop yield"""

    try:
        template = "crop_yield_data_upload.html"    #set template name

        #load form based on request type
        if request.method == "GET":
            return render(request, template)

        #get the csv file
        csv_file = request.FILES["file"]

        # validate type of file uploaded
        if not csv_file.name.endswith(".csv") or csv_file == None:
            messages.error(request, "This is not a csv file")

            return redirect("agriStatsApp:crop_yield_upload")

        # read uploaded file
        df = pd.read_csv(csv_file)

        # run structure checks
        results_struct_chk = data_column_check(df, "crop_yield")
        verified_df = results_struct_chk['file']
        status = results_struct_chk['status']

        for f, s in status.items():
            if s == "fail":
                status['STATUS_REPORT'] = "Data column checks FAILED!:"
                messages.error(request, status)
                return redirect("agriStatsApp:crop_yield_upload")

        crops = ['Maize', 'Rice', 'Millet', 'Sorghum', 'Cassava', 'Yam', 'Cocoyam', 'Plantain', 'Groundnut', 'Cowpea', 'Soyabean']

        # unpivot dataframe
        verified_df = pd.melt(verified_df,
                                id_vars=["Region", "Year", "Crop_Category"],
                                value_vars=crops,
                                var_name="Crop_Type",
                                value_name="Yield_Amount"
                                )

        for i in range(len(verified_df)):
            created = Crop_Yield.objects.update_or_create(
                crop_type=verified_df["Crop_Type"][i],
                crop_category=verified_df["Crop_Category"][i],
                region=verified_df["Region"][i],
                value=verified_df["Yield_Amount"][i],
                year = verified_df["Year"][i],
                date_created = datetime.now(),
                date_updated=datetime.now()
            )

        messages.success(request, "All data rows in csv file uploaded successfully!")
        return redirect("agriStatsApp:crop_yield_upload")

    except MultiValueDictKeyError:
        messages.error(request, "No file selected or invalid file")
        return redirect("agriStatsApp:crop_yield_upload")
    except OperationalError:
        messages.error(request, "The database is locked or table is not available!")
        return redirect("agriStatsApp:crop_yield_upload")
    except IntegrityError:
        messages.error(request, "Duplicates in dataset. Data integrity checks failed!")
        return redirect("agriStatsApp:crop_yield_upload")
    else:
        render(request, template)


#**********************************************************************
#* LOAD PRODUCTION
#**********************************************************************
# CROP PRODUCTION PREVIEW LOAD

@login_required
def CropProductionLoadPreview(request):
    """Load production"""

    try:
        # load form based on request type
        if request.method == "POST":

            # error status report dictionary
            status = {}

            # get the csv file
            file = request.FILES["file"]

            # *** CHECK #1 run file extension #1 ***
            results = file_extension_check(file.name)
            file_extension_report = results['status']

            for f, s in file_extension_report.items():
                if s == "fail":
                    file_extension_report['STATUS_REPORT'] = "File extension checks failed:"
                    messages.error(request, file_extension_report)
                    return redirect("agriStatsApp:crop_production_upload_preview")

            # *** CHECK #2 run file type checks ***
            results = file_type_check(file.name, "crop_production")
            file_type_check_report = results['status']

            for f, s in file_type_check_report.items():
                if s == "fail":
                    file_type_check_report['STATUS_REPORT'] = "File type checks failed:"
                    messages.error(request, file_type_check_report)
                    return redirect("agriStatsApp:crop_production_upload_preview")

            uploadedfile = file.name
            df = pd.read_csv(file)  # read uploaded file

            # *** CHECK #3 run data column checks ***
            results = data_column_check(df, "crop_production")
            data_column_check_report = results['status']

            for f, s in data_column_check_report.items():
                if s == "fail":
                    data_column_check_report['STATUS_REPORT'] = "Data columns checks failed:"
                    messages.error(request, data_column_check_report)
                    return redirect("agriStatsApp:crop_production_upload_preview")

            crops = [
                'Maize', 'Rice', 'Millet', 'Sorghum', 'Cassava', 'Yam',
                'Cocoyam', 'Plantain', 'Groundnut', 'Cowpea', 'Soyabean'
            ]

            # unpivot dataframe
            df = pd.melt(df,
                         id_vars=["Region", "Year", "Crop_Category"],
                         value_vars=crops,
                         var_name="Crop_Type",
                         value_name="Quantity"
                         )

            df_html = df.to_html(table_id="test",
                                 classes=["table-bordered", "table-striped", "table-hover", "display nowrap"])

            request.session['data_frame'] = df.to_dict('records')
            request.session['filename'] = file.name
            request.session['total_rows'] = len(df)

            template = "crop_production_data_upload_preview.html"  # set template name
            context = {
                'uploadedfilename': uploadedfile,
                'data_html': df_html
            }

            return render(request, template, context)
        else:
            template = "crop_production_data_upload_preview.html"  # set template name

            return render(request, template)
    except AttributeError as error:
            status['STATUS_REPORT'] = "Error in file type check! -" + str(error)
            messages.add_message(request, messages.ERROR, status)

            return redirect("agriStatsApp:crop_production_upload_preview")


# CROP PRODUCTION LOAD
def CropProductionLoad(request):
    """Upload of commodities"""

    template = "crop_production_data_upload.html"
    status = {}

    if request.method == 'GET':
        data_frame_dic = request.session.get('data_frame')
        df = pd.DataFrame(data_frame_dic)

        filename = request.session.get('filename')
        type_of_file = 'Commodity Prices'

        total_rows = request.session.get('total_rows')
        upload_date = datetime.now()

        context = {
            'filename': filename,
            'type_of_file': type_of_file,
            'total_rows': total_rows,
            'upload_date': upload_date
        }

        return render(request, template, context)
    else:
        # POST method - uppload data

        data_frame_dic = request.session.get('data_frame')
        df = pd.DataFrame(data_frame_dic)
        df = df.fillna(-1)

        try:
            # save data
            for i in range(len(df)):
                created = Crop_Production.objects.update_or_create(
                    crop_type=df["Crop_Type"][i],
                    crop_category=df["Crop_Category"][i],
                    region=df["Region"][i],
                    value=df["Quantity"][i],
                    year = df["Year"][i],
                    date_created = datetime.now(),
                    date_updated=datetime.now()
                )

        except KeyError as error:
            status['STATUS_REPORT'] = "Data Duplication Error! -" + str(error)
            messages.add_message(request, messages.ERROR, status)
            return redirect("agriStatsApp:crop_production_upload")
        except MultiValueDictKeyError:
            messages.error(request, "No file selected or invalid file")
            return redirect("agriStatsApp:crop_production_upload")
        except OperationalError:
            messages.error(request, "The database is locked or table is not available!")
            return redirect("agriStatsApp:crop_production_upload")
        except IntegrityError:
            messages.error(request, "Duplicates in dataset. Data integrity checks failed!")
            return redirect("agriStatsApp:crop_production_upload")
        else:
            messages.success(request, "All data rows in csv file uploaded successfully!")
            return redirect("agriStatsApp:crop_production_upload")



#*********************************************************************
#* CHECK FOR DUPLICATES
#**********************************************************************
def IsComodityExist(commodity, year, month):
    #get commodity
    commodity = Commodity_Price.objects.get(commodity_name=commodity, year=year, month=month)

#**************************************?melt*******************************
#* SEARCH RETAIl PRICE STATISTICS
#*********************************************************************
def PriceStatisticSearch(request):
    """Search and display commodities and prices"""

    context = {}

    # check request type

    #********************************************************************
    #* GET REQUEST WITH FORM SUBMIT
    #********************************************************************
    #print(request.method)
    if request.method == "GET":

        sel_commodities = None
        year = None
        month = None
        price_category = None

        plot_data = []
        chart = None
        fig = None
        highest_price = None
        lowest_price = None
        highest_price_commodity = None
        lowest_price_commodity = None
        mean_price = None
        total_rows = None
        search_form = None

        # if search contain parameters and values
        if len(request.GET) > 0:

            # submit GET request
            search_form = SearchPrice(request.GET)
            if search_form.is_valid():
                sel_commodities = search_form.cleaned_data.get("commodity")
                year = search_form.cleaned_data.get("year")
                month = search_form.cleaned_data.get("month")
                price_category = search_form.cleaned_data.get("price_category")

                #print(sel_commodities, year, month, price_category)

                year = [int(x) for x in year]

                if "All" not in month:

                    # generate search data for display
                    # ********************************************************

                    # commodity details
                    def_commodity = Commodity_Name.objects.filter(commodity_code__in=sel_commodities)
                    df_def_commodity = pd.DataFrame(def_commodity.values())
                    #print(df_def_commodity.head(n=40))

                    # price details
                    def_price = Commodity_Price.objects.filter(commodity__in=sel_commodities)
                    df_def_price = pd.DataFrame(def_price.values())
                    #print(df_def_price.head(n=40))

                    # merge commodity and price data
                    df_merge = pd.merge(df_def_commodity, df_def_price, left_on='commodity_code',
                                        right_on="commodity_id",
                                        how="inner")


                    if 'all' in month:
                        pass
                    else:
                        df_merge = df_merge[df_merge['month'].isin(month)]

                    if 'all' in price_category:
                        pass
                    else:
                        df_merge = df_merge[df_merge['price_category'].isin(price_category)]

                    # # summary statistics
                    total_rows = len(df_merge)
                    highest_price = df_merge["price"].max()
                    lowest_price = df_merge["price"].min()

                    #print(df_merge)
                    if total_rows > 0:
                        highest_price_commodity = \<div class="card-body">
                            {{ search_inmate_form }}
                    
                        </div>
                            df_merge[df_merge["price"] == df_merge["price"].max()]["commodity_name"].reset_index(
                                drop=True)[0]
                        lowest_price_commodity = df_merge[df_merge["price"] == df_merge["price"].min()][
                            "commodity_name"].reset_index(drop=True)[0]
                        mean_price = '{0:.1f}'.format(df_merge["price"].mean())
                        median_price = '{0:.1f}'.format(df_merge["price"].median())

                        # plot
                        fig = px.line(data_frame=df_merge,
                                      x="month_year",
                                      y="price",
                                      facet_col="price_category",
                                      # symbol="category_type",
                                      color="commodity_name",
                                      line_shape="spline",
                                      title='Price Statistics - price/kg in GHC (Ghana Cedis), of Commodities (National, 2019-2021) <br> Source:  ' \
                                            'Statistics, Research and Info. Directorate (SRID), Min. of Food & Agric.- June, 2021',
                                      color_discrete_map=color_map
                                      )
                        #
                        # fig.add_scatter(x=pdata['month_year'], y=pdata['price'], mode='lines')
                        # fig.show()
                        fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
                        fig.update_xaxes(tickangle=30)
                        fig.update_traces(line=dict(width=3.0))
                        fig.update_layout({
                            'legend_title': "Category",
                            'plot_bgcolor': 'rgba(0, 0, 0, 0)',
                            'paper_bgcolor': 'rgba(0, 0, 0, 0)',
                        })

                        chart = plot(fig, output_type="div",
                                     config={"displayModeBar": True,
                                             "display<div class="card-body">
                            {{ search_inmate_form }}
                    
                        </div>logo": False,
                                             'modeBarButtonsToRemove': [
                                                 'zoom2d',
                                                 'toggleSpikelines',
                                                 'pan2d',
                                                 'select2d',
                                                 'lasso2d',
                                                 'autoScale2d',
                                                 'hoverClosestCartesian',
                                                 'hoverCompareCartesian',
                                                 'resetScale2d'
                                             ]}
                                     )


                        month_ranks = {'January': 1, 'February': 2, 'March': 3, 'April': 4,
                                       'May': 5, 'June': 6, 'July': 7, 'August': 8,
                                       'September': 9, 'October': 10, 'November': 11, 'December': 12
                                       }
                        df_merge['month_rank'] = [int(month_ranks[x]) for x in df_merge['month']]
                        df_merge = df_merge.sort_values(by=['price_category'])
                        df_merge = df_merge[
                            ['commodity_code', 'commodity_name', 'price_category', 'month', 'year', 'price',
                             'month_rank']]
                        df_merge = df_merge.rename(columns={'commodity_code': 'COICOP_CODE',
                                                            'commodity_name': 'COMMODITY',
                                                            'price_category': 'PRICE_CATEGORY',
                                                            'month': 'MONTH',
                                                            'year': 'YEAR',
                                                            'price': 'PRICE'
                                                            })
                    else:
                        df_merge = None

                    html_data_rows = df_merge.to_html(table_id="test",
                                                      classes=["table-bordered", "table-striped", "table-hover"])

                    context = {
                        "Commdity_Names": COMMODITY_NAMES,
                        "Years": YEARS,
                        "Months": MONTHS,

                        "Commodities_html": html_data_rows,

                        #"Commodities": df_merge,
                        "Plot_Div": chart,
                        "Highest_Price": highest_price,
                        "Lowest_Price": lowest_price,
                        "Highest_Price_Commodiy": highest_price_commodity,
                        "Lowest_Price_Commodiy": lowest_price_commodity,
                        "Mean_Price": mean_price,
                        "Median_Price": median_price,
                        "Total_Rows": total_rows,

                        # form variables
                        "Search_Form": search_form,

                    }


                    # template names
                    template = "commodiy_prices_search.html"
                    return render(request, template, context)

        else:
            # no data
            # **************************************************
            # * DEFAULT GET REQUEST
            # **************************************************

            # print('default submit')
            search_form = SearchPrice(request.GET or None,
                                      initial={'commodity': ['117101'],
                                                'year': '2019',
                                                'month': ['all'],
                                                'price_category': ['all']
                                               })


            # generate default data for display
            # **************************************************

            # commodity details
            try:
                def_commodity = Commodity_Name.objects.filter(commodity_name="Ademe/Ayoyo (jute mallow)")
                df_def_commodity = pd.DataFrame(def_commodity.values())

                if len(df_def_commodity) > 0:
                    commodity_code = df_def_commodity['commodity_code'][0]

                    # price details
                    def_price = Commodity_Price.objects.filter(commodity=commodity_code)
                    df_def_price = pd.DataFrame(def_price.values())
                    # merge commodity and price data
                    df_merge = pd.merge(df_def_commodity, df_def_price, left_on='commodity_code',
                                        right_on="commodity_id", how="right")

                    df_merge = df_merge[df_merge['price_category'] == 'retail']

                    total_rows = len(df_merge)
                    highest_price = df_merge["price"].max()
                    lowest_price = df_merge["price"].min()
                    highest_price_commodity = \
                        df_merge[df_merge["price"] == df_merge["price"].max()]["commodity_name"].reset_index(
                            drop=True)[0]
                    lowest_price_commodity = df_merge[df_merge["price"] == df_merge["price"].min()][
                        "commodity_name"].reset_index(drop=True)[0]
                    mean_price = '{0:.1f}'.format(df_merge["price"].mean())
                    median_price = '{0:.1f}'.format(df_merge["price"].median())

                    #
                    # # plot
                    fig = px.line(data_frame=df_merge,
                                  x="month_year",
                                  y="price",
                                  facet_col="price_category",
                                  # symbol="category_type",
                                  color="commodity_name",
                                  line_shape="spline",
                                  title='Price Statistics - price/kg in GHC (Ghana Cedis), of Commodities (National, 2019-2021) <br> Source:  ' \
                                        'Statistics, Research and Info. Directorate (SRID), Min. of Food & Agric.- June, 2021',
                                  color_discrete_map=color_map
                                  )
                    #
                    # fig.add_scatter(x=pdata['month_year'], y=pdata['price'], mode='lines')
                    # fig.show()
                    fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
                    fig.update_xaxes(tickangle=30)
                    fig.update_traces(line=dict(width=3.0))
                    fig.update_layout({
                        'legend_title': "Category",
                        'plot_bgcolor': 'rgba(0, 0, 0, 0)',
                        'paper_bgcolor': 'rgba(0, 0, 0, 0)',
                    })

                    chart = plot(fig,
                                 output_type="div",
                                 config={"displayModeBar": True,
                                         "displaylogo": False,
                                         'modeBarButtonsToRemove': [
                                             'zoom2d',
                                             'toggleSpikelines',
                                             'pan2d',
                                             'select2d',
                                             'lasso2d',
                                             'autoScale2d',
                                             'hoverClosestCartesian',
                                             'hoverCompareCartesian',
                                             'resetScale2d'
                                         ]}
                                 )

                    df_merge = df_merge[['main_category_name',
                                         'sub_category_name',
                                         'commodity_id',
                                         'commodity_name',
                                         'price_category',
                                         'month_year',
                                         'price']]
                    df_merge = df_merge.rename(
                        columns={
                            'main_category_name': 'MAIN_CATEGORY',
                            'sub_category_name': 'SUB_CATEGORY',
                            'commodity_id': 'COICOP_CODE',
                            'commodity_name': 'COMMODITY',
                            'price_category': 'PRICE_TYPE',
                            'month_year': 'MONTH',
                            'year': 'YEAR',
                            'price': 'PRICE'
                            })

                    html_data_rows = df_merge.to_html(table_id="test",
                                                      classes=["table-bordered", "table-striped", "table-hover"])

                    context = {
                        # form variable
                        "Search_Form": search_form,

                        "Commdity_Names": COMMODITY_NAMES,
                        "Years": YEARS,
                        "Months": MONTHS,

                        "Commodities_html": html_data_rows,
                        #"Commodities": df_merge,
                        "Plot_Div": chart,
                        "Highest_Price": highest_price,
                        "Lowest_Price": lowest_price,
                        "Highest_Price_Commodiy": highest_price_commodity,
                        "Lowest_Price_Commodiy": lowest_price_commodity,
                        "Mean_Price": mean_price,
                        "Median_Price": median_price,
                        "Total_Rows": total_rows,
                    }

                    request.session['commodities'] = df_merge.to_json()

                    # template names
                    template = "commodiy_prices_search.html"
                    return render(request, template, context)

            except KeyError:
                template = "commodiy_prices_search.html"
                messages.error(request, "No Record(s)!")

                return render(request, template, context)
                #return redirect("agriStatsApp:commodity_prices_search")


#*********************************************************************
#* SEARCH CROP PRODUCTION
#*********************************************************************
def CropProductionSearch(request):
    """Search and display crop production data"""

    context = {}

    # get request type
    if request.method == "GET":

        if len(request.GET) > 0:
            # perform search

            # extract search variables
            crop_type = request.GET.getlist('crop')
            region = request.GET.getlist('region')
            year = request.GET.get('year')

            data_rows = Crop_Production.objects.filter(crop_type__in=crop_type, region__in=region, year=year)

            df_data_rows = pd.DataFrame(data_rows.values('crop_type', 'region', 'year', 'value'))
            html_data_rows = df_data_rows.to_html(table_id="crop_production", classes=["table-bordered", "table-striped", "table-hover"])

            # PLOTS
            #******
            total_rows = len(df_data_rows)
            crops = df_data_rows.columns

            # ***************************************************************
            # PLOTS
            # ****************************************************************

            if total_rows > 0:
                # BAR
                # *****
                fig1 = px.bar(data_frame=df_data_rows,
                              x='region',
                              y='value',
                              color='crop_type',
                              barmode='stack',
                              # color_discrete_map=crop_color_map,
                              # text = "crop_type",
                              title="Crop Production (in metric tonnes)")

                #data_BAR = fig1.to_html()
                fig1.update_traces(textfont_size=9, textangle=0, textposition="inside", cliponaxis=False)
                data_BAR = plot(fig1,
                                #include_plotlyjs=False,
                                output_type="div",
                                config={
                                    "displayModeBar": True,
                                    "displaylogo": False,
                                    'modeBarButtonsToRemove':
                                        [
                                           'zoom2d',
                                           'toggleSpikelines',
                                           'pan2d',
                                           'select2d',
                                           'lasso2d',
                                           'autoScale2d',
                                           'hoverClosestCartesian',
                                           'hoverCompareCartesian',
                                           'resetScale2d'
                                        ]
                                    }
                               )

                # PIE CHARTS
                # ************
                regions = set(x for x in df_data_rows['region'])  # all regions

                fig_list = []  # list of pie plots

                # create list of plots
                for region in regions:
                    fig_list.append(GenerateCropProductionPiePlots(df_data_rows, region))

                # generate plots for display
                data_pie_plot_list = []
                for itx_fig in fig_list:
                    mfig = plot(itx_fig,
                                # include_plotlyjs=False,
                                output_type="div",
                                config={"displayModeBar": True,
                                        "displaylogo": False,
                                        'modeBarButtonsToRemove': [
                                            'zoom2d',
                                            'toggleSpikelines',
                                            'pan2d',
                                            'select2d',
                                            'lasso2d',
                                            'autoScale2d',
                                            'hoverClosestCartesian',
                                            'hoverCompareCartesian',
                                            'resetScale2d'
                                        ]}
                                )

                    data_pie_plot_list.append(mfig)

                # BOX PLOT
                fig2 = px.box(df_data_rows, x='region', y='value', color='region', title='ALL REGIONS')

                data_BOXPLOT = plot(fig2,
                                    # include_plotlyjs=False,
                                    output_type="div",
                                    config={"displayModeBar": True,
                                           "displaylogo": False,
                                           'modeBarButtonsToRemove': [
                                               'zoom2d',
                                               'toggleSpikelines',
                                               'pan2d',
                                               'select2d',
                                               'lasso2d',
                                               'autoScale2d',
                                               'hoverClosestCartesian',
                                               'hoverCompareCartesian',
                                               'resetScale2d'
                                           ]}
                                   )

                # TREE MAP
                df_data_rows = df_data_rows[df_data_rows['value'] != -999]
                #print(df_data_rows[:5])
                fig1_1 = px.treemap(df_data_rows,
                                    path=[px.Constant("Ghana"), 'region', 'crop_type'],
                                    values='value',
                                    color='crop_type',
                                    hover_data=['crop_type'],
                                    color_continuous_scale='RdBu',
                                    color_continuous_midpoint=np.average(df_data_rows['value']))
                fig1_1.update_layout(margin=dict(t=50, l=25, r=25, b=25))
                fig1_1.data[0]['textfont']['color'] = "white"

                crop_production_TREEMAP = plot(fig1_1,
                                               # include_plotlyjs=False,
                                               output_type="div",
                                               config={"displayModeBar": True,
                                                       "displaylogo": False,
                                                       'modeBarButtonsToRemove': [
                                                           'zoom2d',
                                                           'toggleSpikelines',
                                                           'pan2d',
                                                           'select2d',
                                                           'lasso2d',
                                                           'autoScale2d',
                                                           'hoverClosestCartesian',
                                                           'hoverCompareCartesian',
                                                           'resetScale2d'
                                                       ]}
                                               )

                search_form = ProductionByRegionSearchForm(request.GET or None,
                                                           initial={'crop': 'Maize',
                                                                    'region': 'Ahafo',
                                                                    'year': '2022'
                                                                    })

                template = "crop_production_search.html"
                context = {
                    "search_form": search_form,
                    "html_data_rows": html_data_rows,
                    "Crop_Production_BAR": data_BAR,
                    "Crop_Production_BOXPLOT": data_BOXPLOT,
                    # "Crop_Production_TREEMAP": crop_production_TREEMAP,
                    "Crop_Production_PIE_PLOT_List": data_pie_plot_list,
                }

                return render(request, template, context)

        else:
            # default form load

            # set default variables
            crop_type = ['Maize']
            region = ['Ahafo']
            year = ['2022']

            data_rows = Crop_Production.objects.filter(crop_type__in=crop_type, region__in=region, year__in=year)

            df_data_rows = pd.DataFrame(data_rows.values('crop_type', 'region', 'year', 'value'))
            html_data_rows = df_data_rows.to_html(table_id="crop_production",
                                                  classes=["table-bordered", "table-striped", "table-hover"])

            # PLOTS
            # ******
            total_rows = len(df_data_rows)
            crops = df_data_rows.columns

            # ***************************************************************
            # PLOTS
            # ****************************************************************

            if total_rows > 0:
                # BAR
                # *****
                fig1 = px.bar(data_frame=df_data_rows,
                              x='region',
                              y='value',
                              color='crop_type',
                              barmode='stack',
                              # color_discrete_map=crop_color_map,
                              # text = "crop_type",
                              title="Crop Production (in metric tonnes)")

                # data_BAR = fig1.to_html()
                fig1.update_traces(textfont_size=9, textangle=0, textposition="inside", cliponaxis=False)
                data_BAR = plot(fig1,
                                # include_plotlyjs=False,
                                output_type="div",
                                config={
                                    "displayModeBar": True,
                                    "displaylogo": False,
                                    'modeBarButtonsToRemove':
                                        [
                                            'zoom2d',
                                            'toggleSpikelines',
                                            'pan2d',
                                            'select2d',
                                            'lasso2d',
                                            'autoScale2d',
                                            'hoverClosestCartesian',
                                            'hoverCompareCartesian',
                                            'resetScale2d'
                                        ]
                                }
                                )

                # PIE CHARTS
                # ************
                regions = set(x for x in df_data_rows['region'])  # all regions

                fig_list = []  # list of pie plots

                # create list of plots
                for region in regions:
                    fig_list.append(GenerateCropProductionPiePlots(df_data_rows, region))

                # generate plots for display
                data_pie_plot_list = []
                for itx_fig in fig_list:
                    mfig = plot(itx_fig,
                                #include_plotlyjs=False,
                                output_type="div",
                                config={"displayModeBar": True,
                                        "displaylogo": False,
                                        'modeBarButtonsToRemove': [
                                            'zoom2d',
                                            'toggleSpikelines',
                                            'pan2d',
                                            'select2d',
                                            'lasso2d',
                                            'autoScale2d',
                                            'hoverClosestCartesian',
                                            'hoverCompareCartesian',
                                            'resetScale2d'
                                        ]}
                                )

                    data_pie_plot_list.append(mfig)

                # BOX PLOT
                fig2 = px.box(df_data_rows, x='region', y='value', color='region', title='ALL REGIONS')

                data_BOXPLOT = plot(fig2,
                                    #include_plotlyjs=False,
                                    output_type="div",
                                    config={"displayModeBar": True,
                                            "displaylogo": False,
                                            'modeBarButtonsToRemove': [
                                                'zoom2d',
                                                'toggleSpikelines',
                                                'pan2d',
                                                'select2d',
                                                'lasso2d',
                                                'autoScale2d',
                                                'hoverClosestCartesian',
                                                'hoverCompareCartesian',
                                                'resetScale2d'
                                            ]}
                                    )

                # TREE MAP
                # df_data_rows = df_data_rows[df_data_rows['value'] != -999]
                # print(df_data_rows[:5])
                fig1_1 = px.treemap(df_data_rows,
                                    path=[px.Constant("Ghana"), 'region', 'crop_type'],
                                    values='value',
                                    color='crop_type',
                                    hover_data=['crop_type'],
                                    color_continuous_scale='RdBu',
                                    color_continuous_midpoint=np.average(df_data_rows['value']))
                fig1_1.update_layout(margin=dict(t=50, l=25, r=25, b=25))
                fig1_1.data[0]['textfont']['color'] = "white"

                crop_production_TREEMAP = plot(fig1_1,
                                               #include_plotlyjs=False,
                                               output_type="div",
                                               config={"displayModeBar": True,
                                                       "displaylogo": False,
                                                       'modeBarButtonsToRemove': [
                                                           'zoom2d',
                                                           'toggleSpikelines',
                                                           'pan2d',
                                                           'select2d',
                                                           'lasso2d',
                                                           'autoScale2d',
                                                           'hoverClosestCartesian',
                                                           'hoverCompareCartesian',
                                                           'resetScale2d'
                                                       ]}
                                               )

                search_form = ProductionByRegionSearchForm(request.GET or None,
                       initial={'crop': 'Maize',
                                'region': 'Ahafo',
                                'year': '2022'
                                })

                template = "crop_production_search.html"
                context = {
                    "search_form": search_form,
                    "html_data_rows": html_data_rows,
                    "Crop_Production_BAR": data_BAR,
                    "Crop_Production_BOXPLOT": data_BOXPLOT,
                    "Crop_Production_PIE_PLOT_List": data_pie_plot_list,
                    # "Crop_Production_TREEMAP": crop_production_TREEMAP
                }

                return render(request, template, context)

        template = "crop_production_search.html"
        return render(request, template, context)


# GENERATE PIE PLOTS PER REGION - PRODUCTION
def GenerateCropProductionPiePlots(df, region):

    df = df[df['region'] == region]
    fig = px.pie(df, values='value', names='crop_type', color_discrete_map=crop_color_map, title=region.upper())

    return fig

# GENERATE PIE PLOTS PER REGION - CROP YIELD
def GenerateCropYieldPiePlots(df, region):

    df = df[df['region'] == region]
    fig = px.pie(df, values='value', names='crop_type', title=region.upper())

    return fig

#*********************************************************************
#* CREATE PRODUCTION PLOTS
#*********************************************************************
def CropProductionPlot(request):
    """Display Plots and Statistics from Crop Production Data"""

    if request.method == 'GET': # process form
        crop_production_queryset = Crop_Production.objects.all()    #retrieve cropped area data
        crop_production_df = pd.DataFrame(crop_production_queryset.values())

        total_rows = 0

        #print(len(crop_production_df))

        # are there data rows?
        if len(crop_production_df) > 0:

            total_rows = len(crop_production_df)

            crop_production_df = crop_production_df.fillna(-999)  # change NAs to -999
            crops = crop_production_df.columns[1:-2]

            #***************************************************************
            # CROP PRODUCTION
            #****************************************************************

            # BAR
            #*****
            fig1 = px.bar(crop_production_df,
                          x='region',
                          y='value',
                          color='crop_type',
                          barmode='stack',
                          color_discrete_map=crop_color_map,
                          # text = "crop_type",
                          title="Crop Production (in metric tonnes)")

            fig1.update_traces(textfont_size=9, textangle=0, textposition="inside", cliponaxis=False)
            crop_production_BAR = plot(fig1,
                                    # include_plotlyjs=False,
                                    output_type="div",
                                    config={"displayModeBar": True,
                                           "displaylogo": False,
                                           'modeBarButtonsToRemove': [
                                               'zoom2d',
                                               'toggleSpikelines',
                                               'pan2d',
                                               'select2d',
                                               'lasso2d',
                                               'autoScale2d',
                                               'hoverClosestCartesian',
                                               'hoverCompareCartesian',
                                               'resetScale2d'
                                           ]}
                                    )

            # HIGHEST 5/LOWEST 5 PRODUCTION
            #******************************
            hl_crop_production_df = crop_production_df.groupby(['region', 'crop_type']).mean('value')
            hl_crop_production_df = hl_crop_production_df.reset_index()
            hl_crop_production_df = hl_crop_production_df[(hl_crop_production_df['value'] != -999)]
            #print(hl_crop_production_df)

            hl_crop_production_df = hl_crop_production_df.sort_values(by='value', ascending=False)

            highest_crop_production_df = hl_crop_production_df[:5]
            lowest_crop_production_df = hl_crop_production_df[-5:-1]


            # highest 5
            fig_highest_5_production = px.bar(highest_crop_production_df,
                                              x='region',
                                              y='value',
                                              color='crop_type',
                                              color_discrete_map=crop_color_map,
                                              title="Highest 5 Crops Produced"
                                              )

            highest_5_production_BAR = plot(fig_highest_5_production,
                                            # include_plotlyjs=False,
                                            output_type="div",
                                            config={"displayModeBar": True,
                                                   "displaylogo": False,
                                                   'modeBarButtonsToRemove': [
                                                       'zoom2d',
                                                       'toggleSpikelines',
                                                       'pan2d',
                                                       'select2d',
                                                       'lasso2d',
                                                       'autoScale2d',
                                                       'hoverClosestCartesian',
                                                       'hoverCompareCartesian',
                                                       'resetScale2d'
                                                   ]}
                                            )


            # lowest 5
            fig_least_5_production = px.bar(lowest_crop_production_df,
                                              x='region',
                                              y='value',
                                              color='crop_type',
                                              barmode='stack',
                                              color_discrete_map=crop_color_map,
                                              # text = "crop_type",
                                              title="Lowest 5 Crops Produced"
                                              )

            least_5_production_BAR = plot(fig_least_5_production,
                                        output_type="div",
                                        # include_plotlyjs=False,
                                        config={"displayModeBar": True,
                                                "displaylogo": False,
                                                'modeBarButtonsToRemove': [
                                                    'zoom2d',
                                                    'toggleSpikelines',
                                                    'pan2d',
                                                    'select2d',
                                                    'lasso2d',
                                                    'autoScale2d',
                                                    'hoverClosestCartesian',
                                                    'hoverCompareCartesian',
                                                    'resetScale2d'
                                                ]}
                                        )


            # PIE CHARTS
            #************
            regions = set(x for x in crop_production_df['region']) #all regions

            fig_list = {}   # list of stacked bar plots

            # create list of plots
            for region in regions:
                fig_list[region] = GenerateCropProductionPiePlots(crop_production_df, region)

            #generate plots for display
            crop_production_pie_plot_dic = {}
            for reg, itx_fig in fig_list.items():
                mfig = plot(itx_fig,
                            # include_plotlyjs=False,
                            output_type="div",
                            config={"displayModeBar": True,
                                   "displaylogo": False,
                                   'modeBarButtonsToRemove': [
                                       'zoom2d',
                                       'toggleSpikelines',
                                       'pan2d',
                                       'select2d',
                                        'lasso2d',
                                       'autoScale2d',
                                       'hoverClosestCartesian',
                                       'hoverCompareCartesian',
                                       'resetScale2d'
                                   ]}
                            )

                crop_production_pie_plot_dic[reg] = mfig

            # TREE MAP
            crop_production_df_tm = crop_production_df[crop_production_df['value'] != -999]
            fig1_1 = px.treemap(crop_production_df_tm,
                             path=[px.Constant("Ghana"), 'region', 'crop_type'],
                             values='value',
                             color='crop_type',
                             color_discrete_map=crop_color_map,
                             hover_data=['crop_type'],
                             color_continuous_scale='RdBu',
                             color_continuous_midpoint=np.average(crop_production_df_tm['value']))
            fig1_1.update_layout(margin=dict(t=50, l=25, r=25, b=25))
            fig1_1.data[0]['textfont']['color'] = "white"

            crop_production_TREEMAP = plot(fig1_1,
                                           # include_plotlyjs=False,
                                           output_type="div",
                                           config={"displayModeBar": True,
                                                   "displaylogo": False,
                                                   'modeBarButtonsToRemove': [
                                                       'zoom2d',
                                                       'toggleSpikelines',
                                                       'pan2d',
                                                       'select2d',
                                                       'lasso2d',
                                                       'autoScale2d',
                                                       'hoverClosestCartesian',
                                                       'hoverCompareCartesian',
                                                       'resetScale2d'
                                                   ]}
                                           )

            # BOX PLOT
            fig2 = px.box(crop_production_df, x='region', y='value', color='region', title='ALL REGIONS')

            crop_production_BOXPLOT = plot(fig2,
                                    # include_plotlyjs=False,
                                    output_type="div",
                                    config={"displayModeBar": True,
                                           "displaylogo": False,
                                           'modeBarButtonsToRemove': [
                                               'zoom2d',
                                               'toggleSpikelines',
                                               'pan2d',
                                               'select2d',
                                               'lasso2d',
                                               'autoScale2d',
                                               'hoverClosestCartesian',
                                               'hoverCompareCartesian',
                                               'resetScale2d'
                                           ]}
                                    )

            template = 'crop_production_plots_stats.html'
            context = {
                "Crop_Production_BAR": crop_production_BAR,
                "Highest_5_Production_BAR": highest_5_production_BAR,
                "Lowest_5_Production_BAR": least_5_production_BAR,
                "Crop_Production_TREEMAP": crop_production_TREEMAP,
                "Crop_Production_BOXPLOT": crop_production_BOXPLOT,
                "Crop_Production_PIE_PLOTS": crop_production_pie_plot_dic,

                "Total_Rows": total_rows
            }
        else:
            template = 'crop_production_plots_stats.html'
            context = {
                "Status_Message": 'No Records!',
                "Total_Rows": total_rows
            }


    return render(request, template, context)


#*********************************************************************
#* CREATE CROP YIELD PLOTS
#*********************************************************************
def CropYieldPlot(request):
    """Display Plots and Statistics from Crop Yield Data"""

    pass


#*********************************************************************
#* SEARCH CROP YIELD
#*********************************************************************
def CropYieldSearch(request):
    """Search and display crop yield"""

    context = {}

    # get request type
    if request.method == "GET":

        if len(request.GET) > 0:
            # perform search

            # extract search variables
            crop_type = request.GET.getlist('crop')
            region = request.GET.getlist('region')
            year = request.GET.get('year')

            data_rows = Crop_Yield.objects.filter(crop_type__in=crop_type, region__in=region, year=year)
            df_data_rows = pd.DataFrame(data_rows.values('id', 'crop_type', 'region', 'year', 'value'))
            html_data_rows = df_data_rows.to_html(table_id="test",
                                                  classes=["table-bordered", "table-striped", "table-hover"])

            # PLOTS
            # ******
            total_rows = len(df_data_rows)
            crops = df_data_rows.columns

            # ***************************************************************
            # CROP YIELD
            # ****************************************************************

            # BAR
            # *****
            fig1 = px.bar(df_data_rows,
                          x='region',
                          y='value',
                          color='crop_type',
                          barmode='stack',
                          # color_discrete_map=crop_color_map,
                          # text = "crop_type",
                          title="Crop Yield (in metric tonnes)")

            fig1.update_traces(textfont_size=9, textangle=0, textposition="inside", cliponaxis=False)

            data_BAR = plot(fig1,
                            output_type="div",
                            config={"displayModeBar": True,
                                    "displaylogo": False,
                                    'modeBarButtonsToRemove': [
                                        'zoom2d',
                                        'toggleSpikelines',
                                        'pan2d',
                                        'select2d',
                                        'lasso2d',
                                        'autoScale2d',
                                        'hoverClosestCartesian',
                                        'hoverCompareCartesian',
                                        'resetScale2d'
                                    ]}
                            )

            # PIE CHARTS
            # ************
            regions = set(x for x in df_data_rows['region'])  # all regions

            fig_list = []  # list of pie plots

            # create list of plots
            for region in regions:
                fig_list.append(GenerateCropYieldPiePlots(df_data_rows, region))

            # generate plots for display
            data_pie_plot_list = []
            for itx_fig in fig_list:
                mfig = plot(itx_fig,
                            output_type="div",
                            config={"displayModeBar": True,
                                    "displaylogo": False,
                                    'modeBarButtonsToRemove': [
                                        'zoom2d',
                                        'toggleSpikelines',
                                        'pan2d',
                                        'select2d',
                                        'lasso2d',
                                        'autoScale2d',
                                        'hoverClosestCartesian',
                                        'hoverCompareCartesian',
                                        'resetScale2d'
                                    ]}
                            )

                data_pie_plot_list.append(mfig)

            # BOX PLOT
            fig2 = px.box(df_data_rows, x='region', y='value', color='region', title='ALL REGIONS')

            data_BOXPLOT = plot(fig2,
                                output_type="div",
                                config={"displayModeBar": True,
                                        "displaylogo": False,
                                        'modeBarButtonsToRemove': [
                                            'zoom2d',
                                            'toggleSpikelines',
                                            'pan2d',
                                            'select2d',
                                            'lasso2d',
                                            'autoScale2d',
                                            'hoverClosestCartesian',
                                            'hoverCompareCartesian',
                                            'resetScale2d'
                                        ]}
                                )

            # TREE MAP
            df_data_rows = df_data_rows[df_data_rows['value'] != -999]
            fig1_1 = px.treemap(df_data_rows,
                                path=[px.Constant("Ghana"), 'region', 'crop_type'],
                                values='value',
                                color='crop_type',
                                hover_data=['crop_type'],
                                color_continuous_scale='RdBu',
                                color_continuous_midpoint=np.average(df_data_rows['value']))
            fig1_1.update_layout(margin=dict(t=50, l=25, r=25, b=25))
            fig1_1.data[0]['textfont']['color'] = "white"

            crop_Yield_TREEMAP = plot(fig1_1,
                                           output_type="div",
                                           config={"displayModeBar": True,
                                                   "displaylogo": False,
                                                   'modeBarButtonsToRemove': [
                                                       'zoom2d',
                                                       'toggleSpikelines',
                                                       'pan2d',
                                                       'select2d',
                                                       'lasso2d',
                                                       'autoScale2d',
                                                       'hoverClosestCartesian',
                                                       'hoverCompareCartesian',
                                                       'resetScale2d'
                                                   ]}
                                           )

            # instantiate form
            search_form = CropYieldSearch(request.GET)

            template = "crop_Yield_search.html"
            context = {
                "search_form": search_form,
                "html_data_rows": html_data_rows,
                "Crop_Yield_BAR": data_BAR,
                "Crop_Yield_BOXPLOT": data_BOXPLOT,
                "Crop_Yield_PIE_PLOT_List": data_pie_plot_list,
                "Crop_Yield_TREEMAP": crop_Yield_TREEMAP
            }

            return render(request, template, context)

        else:
            # default for load
            search_form = CropYieldSearch()  # instantiate search form
            template = "crop_CropYield_search.html"
            context = {
                "search_form": search_form
            }

            return render(request, template, context)



#**********************************************************************
#* MODIFY COMMODITY PRICES
#**********************************************************************
@login_required
def ModifyPriceStatisticSearch(request):
    """Search and modify commodity prices"""

    # get commodity names
    COMMODITY_NAMES = Commodity_Name.objects.all()

    # get years
    YEARS = [x for x in range(2019, 2023)]

    # get months
    MONTHS = []
    for i in range(1, 12):
        MONTHS.append(calendar.month_name[i])

    # context variables for template
    context = {
        "Commodity_Names": COMMODITY_NAMES,
        "Years": YEARS,
        "Months": MONTHS
    }

    # template names
    template = "commodity_prices_modify_home.html"

    # check request type
    if request.method == "GET":

        # GET
        commodity_names = Commodity_Name.objects.all()

        context = {
            "Commodity_Names": commodity_names,
            "Years": YEARS,
            "Months": MONTHS,
        }

        # generate default data for display
        commodities = Commodity_Price.objects.filter(commodity_id="117808", year=2019)

        context = {
            "Commodity_Names": commodity_names,
            "Years": YEARS,
            "Months": MONTHS,
            "Commodities": commodities,
        }
        # # print(commodity_name, year, month)

        return render(request, template, context)

    if request.method == "POST":
        # POST

        # commodity names for dropdown
        commodity_names = Commodity_Name.objects.all()

        # get values search criteria
        commodity_name = request.POST.getlist('commodity_name')
        year = request.POST.get('year')
        month = request.POST.get('month')

        if month == "All":
            commodities = Commodity_Price.objects.filter(commodity_name__in=commodity_name, year=year)
        else:
            commodities = Commodity_Price.objects.filter(commodity_name__in=commodity_name, year=year, month=month)

        if len(commodities) > 0:

            context = {
                "Commodity_Names": commodity_names,
                "Years": YEARS,
                "Months": MONTHS,
                "Commodities": commodities,
            }

        return render(request, template, context)

def ModifyCommodity(request):

    modify_commodity_form= CommodityModify(initial={'year': 'Select'})
    template = 'commodity_prices_modify.html'

    context = {"form": modify_commodity_form}

    return render(request, template_name=template, context=context)

def CommodityPricesWholesale(request):
    """View function for commodity prices wholesale home page"""

    return render(request, "commodity_retail.html")

class CommodityPricesViewSet(viewsets.ModelViewSet):
    serializer_class = CommoditySerializer
    queryset = Commodity_Price.objects.all()

#**********************************************************************
#  LOAD COMMODITY PRICES
#**********************************************************************
@login_required
def LoadProductionEstimatesReg(request):
    """Upload commodity wholesale prices"""

    try:
        template = "production_estimates_reg_upload.html"    #set template name

        #load form based on request type
        if request.method == "GET":
            return render(request, template)

        #get the csv file
        csv_file = request.FILES["file"]

        #validate type of file uploaded
        if not csv_file.name.endswith(".csv") or csv_file == None:
            messages.error(request, "This is not a csv file")

            return redirect("agriStatsApp:production_estimate_reg_upload")

        #read uploaded file
        df = pd.read_csv(csv_file)

        #run structure checks
        # df.columns = [x.strip() for x in df.columns]
        results = file_type_check(df, "production_estimate_reg")
        verified_df = results['file']
        status = results['status']

        for f, s in status.items():
            if s == "fail":
                status['STATUS_REPORT'] = "File structure checks failed:"
                messages.error(request, status)
                return redirect("agriStatsApp:production_estimates_reg_upload")

        crop_types = [
            col for col in df.columns
        ]

        # pivot the data
        try:
            #pivot longer
            verified_df_2 = pd.melt(verified_df,
                                    id_vars=["Region", "Unit", "Quantity"],
                                    value_vars=crop_types,
                                    var_name="Month",
                                    value_name="Price"
                                    )

            #transform month field to a time series
            #verified_df_2['Year'] = verified_df_2['Year'].fillna(0).astype('int')
            verified_df_2['Month_Year'] = list(map(setTime, verified_df_2['Month'], verified_df_2['Year'].fillna(0).astype('int')))

            # save data
            for i in range(len(verified_df_2)):
                created = Commodity_Price.objects.update_or_create(
                    commodity_code=verified_df_2["commodity_code"][i],
                    commodity_name=verified_df_2["Commodity_Name"][i],
                    category_type=verified_df_2["Category_Type"][i],
                    year=verified_df_2["Year"][i],
                    unit=verified_df_2["Unit"][i],
                    quantity=verified_df_2["Quantity"][i],
                    month=verified_df_2["Month"][i],
                    month_year = verified_df_2["Month_Year"][i],
                    price=verified_df_2["Price"][i],
                    date_updated=datetime.now()
                )

        except KeyError as error:
            status['STATUS_REPORT'] = error
            messages.add_message(request, messages.ERROR, status)

            return redirect("agriStatsApp:commodity_prices_upload")
        except ProgrammingError as error:
            status['STATUS_REPORT'] = "Nan values in dataset"
            messages.add_message(request, messages.ERROR, status)

            return redirect("agriStatsApp:commodity_prices_upload")
        else:
            context = {}
            messages.success(request, "All data rows in csv file uploaded successfully!")

        return redirect("agriStatsApp:commodity_prices_upload")

    except MultiValueDictKeyError:
        messages.error(request, "No file selected or invalid file")
        return redirect("agriStatsApp:commodity_prices_upload")
    except OperationalError:
        messages.error(request, "The database is locked or table is not available!")
        return redirect("agriStatsApp:commodity_prices_upload")
    else:
        context = {}
        render(request, template, context)

#****************************************************
#* DOWNLOAD DATA FILE
#****************************************************
def DownloadData(request):

    # DownloadData(request, df)
    # create the HttpResponse object with the appropriate csv header
    dic_x = {'names': ['samuel', 'angel', 'miracle'], 'scores': [80, 70, 90]}
    results = pd.DataFrame(dic_x)

    results2 = request.session['commodities']
    results2 = json.loads(results2)
    results2 = pd.DataFrame.from_dict(results2, orient="columns")

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=download.csv'

    results2.to_csv(path_or_buf=response, sep=';', float_format='%.2f', index=False, decimal=",")
    return response

#****************************************************
#* UPLOAD GCA REPORTS
#****************************************************
class UploadGCACreateView(CreateView):
    model = Document_Upload
    form_class = DocumentForm
    template_name = 'docs_upload.html'
    success_url = reverse_lazy('agriStatsApp:gca_docs_list')

# #****************************************************
# #* LIST GCA REPORTS
# #****************************************************
class GCADocsListView(ListView):
    model = Document_Upload
    template_name = 'gca_docs_list.html'
    context_object_name = 'documents'

#****************************************************
#* DOWNLOAD DOCS
#****************************************************
def PDFDownloadListView(request, document_id):
    document = get_object_or_404(Document_Upload, pk=document_id)
    response = HttpResponse(document.document, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename = "{document.document.name}"'

    return response

def XLSDownloadListView(request, document_id):
    document = get_object_or_404(Document_Upload, pk=document_id)
    response = HttpResponse(document.document, content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = f'attachment; filename = "{document.document.name}"'

    return response


#****************************************************
#* PRODUCTION
#****************************************************

#search crop data
class SearchCropData():
    pass

# #upload files
class UploadProductionCreateView(CreateView):
    model = Document_Upload
    form_class = DocumentForm
    template_name = 'docs_upload.html'
    success_url = reverse_lazy('agriStatsApp:crop_production_list')
# #
# #list files
class ProductionListView(ListView):
    model = Document_Upload
    queryset = Document_Upload.objects.filter(document_type = 'production')
    template_name = 'crop_production_list.html'
    context_object_name = 'documents'

#****************************************************
#* DISPLAY MAPS
#****************************************************
def CropProductionMap(request):

    template = "gis_maps.html"
    return render(request, template)
#validate type of file
# if not csv_file.name.endswith(".csv") or csv_file == None:
#     messages.error(request, "This is not a csv file")
#     return redirect("agriStatsApp:commodity_prices_names_upload")
#
# # convert file to unicode
# data_set = csv_file.read().decode('UTF-8')
# io_string = io.StringIO(data_set)   #data stream
#
# # skip first line of csv file
# next(io_string)
#
# for column in csv.reader(io_string, delimiter = ',', quotechar = "|"):
#     _, created = Commodity_Names.objects.update_or_create(
#         main_category_code = column[0].replace('\"', ''),
#         main_category_name = column[1].replace('\"', ''),
#         sub_category_code=column[2].replace('\"', ''),
#         sub_category_name=column[3].replace('\"', ''),
#         commodity_code = column[4].replace('\"', ''),
#         commodity_name = column[5].replace('\"', ''),
#         date_created=datetime.now(),
#         date_updated = None
#     )


# if len(plot_data) > 0:
            #     for pdata in plot_data:

                    #
                    # # Add Scatter plot
                    #commodities_df['month_year']

            # # convert to dataframe
            # pdata = pd.DataFrame(df.values())
            #print(pdata)
            # fig = px.line()
            # fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
            # fig.show()
            # print(commodities_df['category_type'])

            #
            # print("Has data...", commodities_df)
            #

# if len(df_2020_retail) > 0 or len(df_2020_wholesale) > 0:
#     merged_2020_retail = pd.merge(df_2020_retail, df_commodities, left_on='commodity_code',
#                                   right_on="commodity_code", how="inner")
#     merged_2020_wholesale = pd.merge(df_2020_wholesale, df_commodities, left_on='commodity_code',
#                                      right_on="commodity_code", how="inner")
#
#     months = [
#         'January',
#         'February',
#         'March',
#         'April',
#         'May',
#         'June',
#         'July',
#         'August',
#         'September',
#         'October',
#         'November',
#         'December'
#     ]
#
#     # merged_2019_df
#     final_df = pd.concat([merged_2020_retail, merged_2020_wholesale], axis=0)
#
#     final_df = merged_2020_retail
#     commodities_2020_retail = set([i for i in merged_2020_retail['commodity_name_x']])
#     commodities_2020_wholesale = set([i for i in merged_2020_wholesale['commodity_name_x']])
#     all_commodities = set.intersection(commodities_2020_retail, commodities_2019_wholesale)
#
#     final_df = final_df[final_df['commodity_name_x'].isin(all_commodities)]
#
#     commodities = (
#         final_df.sort_values(by=['price'])['commodity_name_x'].unique()
#     )
#
#     data_1 = {'line_x': [], 'line_y': [], 'retail': [], 'wholesale': []}
#
#     for commodity in commodities:
#         data_1['retail'].extend([final_df.loc[(final_df['category_type'] == 'retail') & (
#                     final_df['commodity_name_x'] == commodity)][
#                                      'price'].values.mean()])
#         data_1['wholesale'].extend([final_df.loc[(final_df['category_type'] == 'wholesale') & (
#                     final_df['commodity_name_x'] == commodity)][
#                                         'price'].values.mean()])
#         data_1["line_x"].extend(
#             [
#                 final_df.loc[
#                     (final_df['category_type'] == 'retail') & (final_df['commodity_name_x'] == commodity)][
#                     'price'].values.mean(),
#                 final_df.loc[
#                     (final_df['category_type'] == 'wholesale') & (final_df['commodity_name_x'] == commodity)][
#                     'price'].values.mean(),
#                 None,
#             ]
#         )
#         data_1["line_y"].extend([commodity, commodity, None]),
#
#     fig2 = go.Figure(
#         data=[
#             go.Scatter(
#                 x=data_1["line_x"],
#                 y=data_1["line_y"],
#                 mode="lines",
#                 showlegend=False,
#                 marker=dict(color="green", size=10)
#             ),
#             go.Scatter(
#                 x=data_1["retail"],
#                 y=commodities,
#                 mode="markers",
#                 name="Retail",
#                 marker=dict(
#                     color="green",
#                     size=10
#                 )
#             ),
#             go.Scatter(
#                 x=data_1["wholesale"],
#                 y=commodities,
#                 mode="markers",
#                 name="Wholesale",
#                 marker=dict(
#                     color="blue",
#                     size=10
#                 )
#             ),
#         ]
#     )
#
#     fig2.update_layout(
#         title="Mean Price Changes for Wholesale and Retail (2019)",
#         height=1200,
#         width=1300,
#         legend_itemclick=False
#     )
#
#     dumb_bell = plot(fig2, output_type="div")
#
#     # End of the Dumb Bell Plot
#     # ***********************************************************************************************************************************

    #
    #
    # #
    #     # top 10 least expensive wholesale commodities in 2019
    #     merged_2019_wholesale_grp_df = merged_2019_wholesale.groupby(['commodity_name_x', 'year'])[
    #         'price'].mean().reset_index()
    #     df_10_most_expensive = merged_2019_wholesale_grp_df.sort_values(by=['price'], ascending=True)[:5]
    #     fig2 = px.scatter(df_10_most_expensive, x="price", y="commodity_name_x",
    #                       size="price", color="commodity_name_x",
    #                       hover_name="commodity_name_x", log_x=True, size_max=60,
    #                       title="Top 10 least expensive wholesale commodities in 2019",
    #                       labels={'price': 'Price', 'commodity_name_x': 'Commodity'})
    #
    #     bubble_2 = plot(fig2, output_type="div")
    #
    #     # top 10 most expensive wholesale commodities in 2020
    #     merged_2020_wholesale_grp_df = merged_2020_wholesale.groupby(['commodity_name_x', 'year'])[
    #         'price'].mean().reset_index()
    #     df_10_most_expensive = merged_2020_wholesale_grp_df.sort_values(by=['price'], ascending=False)[:5]
    #     fig2 = px.scatter(df_10_most_expensive, x="price", y="commodity_name_x",
    #                       size="price", color="commodity_name_x",
    #                       hover_name="commodity_name_x", log_x=True, size_max=60,
    #                       title="Top 10 most expensive wholesale commodities in 2019",
    #                       labels={'price': 'Price', 'commodity_name_x': 'Commodity'},
    #                       color_discrete_map=color_map
    #                       )
    #
    #     bubble_1 = plot(fig2, output_type="div")
    #
    #     # top 10 least expensive wholesale commodities in 2020
    #     merged_2019_wholesale_grp_df = merged_2019_wholesale.groupby(['commodity_name_x', 'year'])[
    #         'price'].mean().reset_index()
    #     df_10_most_expensive = merged_2019_wholesale_grp_df.sort_values(by=['price'], ascending=True)[:5]
    #     fig2 = px.scatter(df_10_most_expensive, x="price", y="commodity_name_x",
    #                       size="price", color="commodity_name_x",
    #                       hover_name="commodity_name_x", log_x=True, size_max=60,
    #                       title="Top 10 least expensive wholesale commodities in 2019",
    #                       labels={'price': 'Price', 'commodity_name_x': 'Commodity'})
    #
    #     bubble_2 = plot(fig2, output_type="div")

    #JSON file serializer
    # from django.core.files.uploadedfile import InMemoryUploadedFile
    # from django.core.serializers.json import DjangoJSONEncoder
    #
    # class MyJsonEncoder(DjangoJSONEncoder):
    #     def default(self, o):
    #         if isinstance(o, InMemoryUploadedFile):
    #             return o.read()
    #         return str(o)

    # results = json.dumps(file, cls=MyJsonEncoder)

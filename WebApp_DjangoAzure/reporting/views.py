from django.shortcuts import render
import pandas as pd
import sqlalchemy
import urllib
import numpy as np


# Create your views here.
def index(request):
    context = create_index_view_content('all')
    return render(request, 'reporting/index.html', context=context)


def mg_other(request):
    context = create_index_view_content('mg_other')
    return render(request, 'reporting/mg_other.html', context=context)


def mg_chf(request):
    context = create_index_view_content('mg_chf')
    return render(request, 'reporting/mg_chf.html', context=context)


def he_other(request):
    context = create_index_view_content('he_other')
    return render(request, 'reporting/he_other.html', context=context)


def get_bardata_highchart(dataset,scenarios):
    tmp_data=[]
    for i in scenarios:
        try:
            tempdf=dataset[dataset['Scenario']==i]
            temp={}
            temp["name"] = 'LGD (' + i + ')'
            temp["data"] = list(tempdf.LGD_new * 100)
            tmp_data.append(temp)
        except:
                pass
    return (tmp_data)


def get_tabulator_columns(dataset):
    tabulator_columns = []

    for i in dataset.columns:
        if i == 'PRD_CATEGORY':
            temp = {}
            temp["title"] = "Product Category"
            temp["field"] = "PRD_CATEGORY"
            temp["editor"] = "input"
            temp["frozen"] = "true"
            tabulator_columns.append(temp)
        elif i == 'CurrGroup':
            temp = {}
            temp["title"] = "Currency"
            temp["field"] = "CurrGroup"
            temp["editor"] = "input"
            tabulator_columns.append(temp)
        elif i == 'DEFAULT_FLAG':
            temp = {}
            temp["title"] = "Default flag"
            temp["field"] = "DEFAULT_FLAG"
            temp["editor"] = "input"
            tabulator_columns.append(temp)
        elif i == 'Band2':
            temp = {}
            temp["title"] = "LTV Band"
            temp["field"] = "Band2"
            temp["editor"] = "input"
            tabulator_columns.append(temp)
        else:
            temp = {}
            temp["title"] = i
            temp["field"] = i
            temp["editor"] = "input"
            tabulator_columns.append(temp)
    return (tabulator_columns)


def create_index_view_content(condition):
    """ view function for sales app """
    server = 'makrinari.database.windows.net'
    db = 'Eurobank_LGD'
    username = 'makrinari'
    password = 'Sm@0323159'
    # create Connection and Cursor objects
    params = 'DRIVER={ODBC Driver 11 for SQL Server}' + ';SERVER=' + server + ';PORT=1433;DATABASE=' + db + ';UID=' + username + ';PWD=' + password
    db_params = urllib.parse.quote_plus(params)
    engine = sqlalchemy.create_engine("mssql+pyodbc:///?odbc_connect={}".format(db_params))

    # read data
    #df = pd.read_csv("C:/Users/Michail Markis/Downloads/car_sales.txt", delimiter=',')
    df = pd.read_sql('MLU_LGD', engine)
    #df['category'] = df['PRD_CATEGORY']+'-' + np.where(df['DEFAULT_FLAG'] == 1,'default','nondefault')

    scenarios = list(pd.unique(df.Scenario))

    he_non_def_other = df[(df['PRD_CATEGORY'] == 'HE') & (df['DEFAULT_FLAG'] == 0)]
    he_categories_non_def_other = list(pd.unique(he_non_def_other.Band2))
    he_values_non_def_other = get_bardata_highchart(he_non_def_other, scenarios)

    he_def_other = df[(df['PRD_CATEGORY'] == 'HE') & (df['DEFAULT_FLAG'] == 0)]
    he_categories_def_other = list(pd.unique(he_def_other.Band2))
    he_values_def_other = get_bardata_highchart(he_def_other, scenarios)

    mg_non_def_other = df[((df['PRD_CATEGORY'] == 'MG') & (df['DEFAULT_FLAG'] == 0) & (df['CurrGroup'] == 'OTHER'))]
    mg_categories_non_def_other = list(pd.unique(mg_non_def_other.Band2))
    mg_values_non_def_other = get_bardata_highchart(mg_non_def_other, scenarios)

    mg_def_other = df[(df['PRD_CATEGORY'] == 'MG') & (df['DEFAULT_FLAG'] == 1) & (df['CurrGroup'] == 'OTHER')]
    mg_categories_def_other = list(pd.unique(mg_def_other.Band2))
    mg_values_def_other = get_bardata_highchart(mg_def_other, scenarios)

    mg_non_def_chf = df[(df['PRD_CATEGORY'] == 'MG') & (df['DEFAULT_FLAG'] == 0) & (df['CurrGroup'] == 'CHF')]
    mg_categories_non_def_chf = list(pd.unique(mg_non_def_chf.Band2))
    mg_values_non_def_chf = get_bardata_highchart(mg_non_def_chf, scenarios)

    mg_def_chf = df[(df['PRD_CATEGORY'] == 'MG') & (df['DEFAULT_FLAG'] == 1) & (df['CurrGroup'] == 'CHF')]
    mg_categories_def_chf = list(pd.unique(mg_def_chf.Band2))
    mg_values_def_chf = get_bardata_highchart(mg_def_chf, scenarios)

    if condition == 'he_other':
        df = df[(df['PRD_CATEGORY'] == 'HE') & (df['CurrGroup'] == 'OTHER')]
    elif condition == 'mg_other':
        df = df[(df['PRD_CATEGORY'] == 'MG') & (df['CurrGroup'] == 'OTHER')]
    elif condition == 'mg_chf':
        df = df[(df['PRD_CATEGORY'] == 'MG') & (df['CurrGroup'] == 'CHF')]
    else:
        df = df

    df = df.sort_values(by=['PRD_CATEGORY', 'CurrGroup', 'DEFAULT_FLAG', 'Band2'], ascending=True)

    df2 = pd.pivot_table(df, values='LGD_new', index=['PRD_CATEGORY', 'CurrGroup', 'Band2', 'DEFAULT_FLAG'],
                         columns='Scenario').reset_index()

    for i in scenarios:
        df2 = df2.rename(columns={i: 'LGD (' + i + ')'})

    df2 = df2.sort_values(by=['PRD_CATEGORY','CurrGroup','DEFAULT_FLAG','Band2'], ascending=True)

    table_data_json = df2.to_json(orient='records')

    table_content = df[['PRD_CATEGORY','CurrGroup','Band2','DEFAULT_FLAG','LGD_new']].to_html(index=None)
    table_content = table_content.replace("", "")
    table_content = table_content.replace('class="dataframe"', "class='table table-striped'")
    table_content = table_content.replace('border="2"', "")

    tabulator_columns = get_tabulator_columns(df2)

    context = {"he_categories_non_def_other": he_categories_non_def_other
                , 'he_values_non_def_other': he_values_non_def_other

                , 'he_categories_def_other': he_categories_def_other
                , 'he_values_def_other': he_values_def_other

                , 'mg_categories_non_def_other': mg_categories_non_def_other
                , 'mg_values_non_def_other': mg_values_non_def_other

                , 'mg_categories_def_other': mg_categories_def_other
                , 'mg_values_def_other': mg_values_def_other

                , 'mg_categories_non_def_chf': mg_categories_non_def_chf
                , 'mg_values_non_def_chf': mg_values_non_def_chf

                , 'mg_categories_def_chf': mg_categories_def_chf
                , 'mg_values_def_chf': mg_values_def_chf

                , 'table_data': table_content
                , 'table_data_json': table_data_json

               , 'scenarios': scenarios
               , 'tabulator_columns': tabulator_columns}
    return (context)

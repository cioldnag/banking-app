import streamlit as st
import pandas as pd
from plotly.subplots import make_subplots
import plotly.express as px
import plotly.graph_objects as go
from re import sub
import numpy as np
from random import randrange
from random import randint
import copy
import math
import matplotlib.pyplot as plt
import datetime
# pd.options.display.max_columns = None
# pd.options.display.max_rows = 100
from datetime import datetime
from datetime import timedelta, date
import os
from dateutil.relativedelta import relativedelta
import timeit


@st.cache_data
def vroumvroum(x):
    start2 = timeit.default_timer()
    data = pd.read_csv(sorted([i for i in os.listdir() if (("-" in i) and i[0]=='2' )])[-1])
    # st.write(sorted([i for i in os.listdir() if (("-" in i) and i[0]=='2' )]))
    data.drop("Unnamed: 0", axis=1, inplace=True)
    data.sort_values(by="Date", inplace=True)

    last_date = data.Date.values[-1]
    # st.write(last_date)
    data_degiro = pd.read_csv(
        "data/" + sorted([i for i in os.listdir("data") if "DEGIRO" in i])[-1])
    data_fortuneo = pd.read_csv("data/" + sorted([i for i in os.listdir(
        "data") if "FORTUNEO" in i])[-1], encoding="ISO-8859-1", delimiter=";")
    data_degiro = data_degiro.rename(columns={"Unnamed: 8": "Amount", "Unnamed: 10": "Balance",
                                     "Beschreibung": "Description", "Saldo": "Currency", "Produkt": "Product"}, errors="raise")
    data_degiro["Amount"].replace(",", ".", regex=True, inplace=True)
    data_degiro["Balance"].replace(",", ".", regex=True, inplace=True)
    data_degiro["FX"].replace(",", ".", regex=True, inplace=True)
    data_degiro["FX"] = data_degiro["FX"].values.astype(float)
    data_degiro["Amount"] = data_degiro["Amount"].values.astype(float)
    data_degiro["Date"] = pd.to_datetime(
        data_degiro["Datum"], infer_datetime_format=True, dayfirst=True)
    data_degiro.drop(columns=["Datum", "Uhrze", "Valutadatum"], inplace=True)
    cols = data_degiro.columns.tolist()
    cols = ['Date', 'Product', 'ISIN', 'Description', 'FX',
            'Änderung', 'Amount', 'Currency', 'Balance', 'Order-ID']
    data_degiro = data_degiro[cols]

    data_degiro = data_degiro[data_degiro["Date"] > last_date]
    data_fortuneo = data_fortuneo.rename(
        columns={"Montant net": "Amount", "libellé": "Product"}, errors="raise")
    data_fortuneo["Date"] = pd.to_datetime(
        data_fortuneo["Date"], infer_datetime_format=True, dayfirst=True)
    data_fortuneo = data_fortuneo[data_fortuneo["Date"] > last_date]

    data_deg = data_degiro.copy()
    div_index = data_deg[(data_deg["Description"] == "Dividende") | (
        data_deg["Description"].str.contains("gleich", na=False))].index
    steuer_index = data_deg[data_deg["Description"].str.contains(
        "teu", regex=True, na=False)].index
    data_div = data_deg.copy()
    steuer_index2 = list(steuer_index.copy())
    # st.write(data_degiro)
    ##################################################  Table for dvidends  ########################################

    table_div = pd.DataFrame(columns=["Date", "Product", "Amount"])
    l_date = []
    l_product = []
    l_amount = []

    from datetime import datetime
    from dateutil.relativedelta import relativedelta
    for i in div_index:
        # print(i)
        fx = 1
        # result=3
        test1 = 3
        test2 = 3
        test3 = 0
        to_sum = []
        for j in steuer_index2:
            test1 = int(data_div.loc[j].Product == data_div.loc[i].Product)
            test2 = int(
                abs((data_div.loc[i].Date-data_div.loc[j].Date).days) < 35)
            if (test1+test2) == 2:
                to_sum.append(j)
            if (((test1+test2) == 0) | ((test1+test2) == 1)):
                # print(i)
                test3 = 0
        if len(to_sum) > 0:  # in case of taxe on the dividend, the taxe & the dividend are sum, then the line is removed

            # print(data_div.loc[i].Date,end="  ****  ")
            l_date.append(data_div.loc[i].Date)

            # print(data_div.loc[i].Product,end="  ****  ")
            l_product.append(data_div.loc[i].Product)
            fx = 1
            if ((data_div.loc[i].Currency) != "EUR"):

                for x in range(i, i-10, -1):
                    if (x < 0):
                        fx = 1
                        break
                    if ((data_deg.loc[x].FX > 0) & (data_deg.loc[x].Currency == data_deg.loc[i].Currency) & (data_deg.loc[x].Description == "Währungswechsel (Ausbuchung)")):
                        fx = data_deg.loc[x].FX
                        break

            # print(((sum([data_div.loc[s].Amount for s in to_sum ])+data_div.loc[i].Amount)/fx).round(2),end=" €")
            l_amount.append(
                ((sum([data_div.loc[s].Amount for s in to_sum])+data_div.loc[i].Amount)/fx).round(2))

            data_div.drop(to_sum, axis=0, inplace=True)
            for t in to_sum:
                steuer_index2.remove(t)
        if ((test3 + len(to_sum)) == 0):  # in case of no taxe
            # print("test3")
            # print(data_div.loc[i].Date,end="  ****  ")
            l_date.append(data_div.loc[i].Date)

            # print(data_div.loc[i].Product,end="  ****  ")
            l_product.append(data_div.loc[i].Product)

            if ((data_div.loc[i].Currency) != "EUR"):

                for x in range(i, i-10, -1):
                    if (x < 0):
                        fx = 1
                        break
                    # print(x)
                    if ((data_deg.loc[x].FX > 0) & (data_deg.loc[x].Currency == data_deg.loc[i].Currency) & (data_deg.loc[x].Description == "Währungswechsel (Ausbuchung)")):
                        fx = data_deg.loc[x].FX
                        break
            # print(((data_div.loc[i].Amount)/fx).round(2),end=" €")
            l_amount.append(((data_div.loc[i].Amount)/fx).round(2))

            # print(data_div.loc[i].Currency)
            # print("***")

    # add the list to the data frame

    table_div["Date"] = l_date
    table_div["Product"] = l_product
    table_div["Amount"] = l_amount
    # print(table_div["Amount"].sum())
    # table_div_deg=table_div.copy()
    table_div = pd.concat([table_div, data_fortuneo[(data_fortuneo["Opération"].str.contains("ncai")) & (
        data_fortuneo["Place"].str.contains("aris|Amst", regex=True, na=False))][["Date", "Product", "Amount"]]])
    table_div = table_div.sort_values(by="Date")
    table_div = table_div.rename(columns={"Amount": "Total"})
    table_div["Description"] = "Dividend"

    ################################# Table for fortuneo transaction########################################

    tr_for = data_fortuneo[(data_fortuneo["Opération"].str.contains("Achat|TAXE|Vente") & (
        data_fortuneo["Place"].str.contains("aris|Amst", regex=True, na=False)))]

    # Date	Product	Description	Price	Currency	Quantity	Taxes	Amount	Total
    # ['ORANGE' 'Achat Comptant' 'Euronext Paris' Timestamp('2016-10-20 00:00:00') 32 '14' '-448' '-1,95' -449.95 'EUR']
    l_date = []
    l_product = []
    l_op = []
    l_quantity = []
    l_prix = []
    l_currency = []
    l_taxes = []
    l_values = []
    l_amount = []
    for i in tr_for.values:
        if ("Vente" in i[1]):
            l_date.append(i[3])
            l_product.append(i[0])
            l_op.append("Vente")
            l_quantity.append(-i[4])
            l_prix.append(float(i[5]))
            l_currency.append("EUR")
            l_taxes.append(float(i[7]))
            l_values.append(i[8]-float(i[7]))
        if ("Achat" in i[1]):
            l_date.append(i[3])
            l_product.append(i[0])
            l_op.append("Achat")
            l_quantity.append(i[4])
            l_prix.append(float(i[5]))
            l_currency.append("EUR")
            tf = 0
            if len(tr_for[((tr_for["Opération"].str.contains("TAXE")) & (tr_for["Date"] == i[3]) & (tr_for["Qté"] == i[4]) & (tr_for["Product"].str.contains(i[0][:6]))) == True].values) == 1:
                # print(tr_for[((tr_for["Opération"].str.contains("TAXE"))&(tr_for["Date"]==i[3])&(tr_for["Qté"]==i[4])&(tr_for["Product"]==i[0]))==True].values[0][8],end=" ")
                tf = tr_for[((tr_for["Opération"].str.contains("TAXE")) & (tr_for["Date"] == i[3]) & (
                    tr_for["Qté"] == i[4]) & (tr_for["Product"] == i[0])) == True].values[0][8]
            l_taxes.append(float(i[7])+tf)
            l_values.append(i[8]-float(i[7]))

    table_for = pd.DataFrame()
    table_for["Date"] = l_date
    table_for["Product"] = l_product
    table_for["Description"] = l_op
    table_for["Price"] = l_prix
    table_for["Currency"] = l_currency
    table_for["Quantity"] = l_quantity
    table_for["Taxes"] = l_taxes
    table_for["Amount"] = l_values
    table_for["Total"] = table_for["Amount"]+table_for["Taxes"]

    ##################################### Table for degiro transaction########################################
    # st.write("212")

    transac = []
    for i in data_deg.index.values:
        # print(type(i))
        if ("gebühren" in str(data_deg.loc[i, "Description"])):
            # print(data_deg.loc[i,"Description"])
            transac.append(i)
        if (("Währungswechsel (Ausbuchung)" in str(data_deg.loc[i, "Description"])) & (~("nan" in str(data_deg.loc[i, "Product"])))):
            if ("EUR" in str(data_deg.loc[i, "Currency"])):
                transac.append(i)
        if (("Währungswechsel (Einbuchung)" in str(data_deg.loc[i, "Description"])) & (~("nan" in str(data_deg.loc[i, "Product"])))):
            if ("EUR" in str(data_deg.loc[i, "Currency"])):
                transac.append(i)
        if (("Kauf" in str(data_deg.loc[i, "Description"])) & (("EUR" in str(data_deg.loc[i, "Currency"])))):
            # print(data_deg.loc[i,"Description"],end=" ")
            # print(data_deg.loc[i,"Product"])
            transac.append(i)
        if (("Verkauf" in str(data_deg.loc[i, "Description"])) & (("EUR" in str(data_deg.loc[i, "Currency"])))):
            # print(data_deg.loc[i,"Description"],end=" ")
            # print(data_deg.loc[i,"Product"])
            transac.append(i)
        if (("Kauf" in str(data_deg.loc[i, "Description"])) & (~("EUR" in str(data_deg.loc[i, "Currency"])))):
            data_deg.loc[i, "Amount"] = 0
            # print(data_deg.loc[i,"Description"],end=" ")
            # print(data_deg.loc[i,"Product"])
            transac.append(i)
        if (("Verkauf" in str(data_deg.loc[i, "Description"])) & (~("EUR" in str(data_deg.loc[i, "Currency"])))):
            data_deg.loc[i, "Amount"] = 0
            # print(data_deg.loc[i,"Description"],end=" ")
            # print(data_deg.loc[i,"Product"])
            transac.append(i)
    # print(data_deg.loc[transac]["Amount"].sum())
    # data_deg.loc[transac][270:370]
    tr_deg = data_deg.loc[transac]
    # tr_deg[:80]
    if (len(tr_deg.index)) > 0:
        try:
            tr_deg["Order-ID"] = tr_deg["Order-ID"].str[:19]
        except:
            tr_deg["Order-ID"] = tr_deg["Order-ID"]
    for i in tr_deg[tr_deg["Order-ID"].isna() & (~tr_deg["Product"].str.contains("STANLEY|FUNDSHAR"))].index:
        tr_deg.loc[i, "Order-ID"] = randint(0, 9999999999999999999999999)

    # tr_deg[tr_deg["Description"].str.contains("SPLIT|ERH")]

    l_date = []
    l_product = []
    l_op = []
    l_quantity = []
    l_prix = []
    l_currency = []
    l_taxes = []
    l_values = []
    l_amount = []
    word = ["DELISTING", "KAPITALERHÖHUNG", "AKTIENSPLIT", "SPIN-OFF"]
    # st.write("264")

    for m in tr_deg[["Order-ID"]].value_counts().index:

        i = tr_deg.loc[tr_deg["Order-ID"] == m[0]]
        l_product.append(i[["Product"]].values[0][0])
        l_date.append(i[["Date"]].values[0][0])
        sum_i = i.loc[i["Description"].str.contains(
            "Ausbuchung|Einbuchung|Kauf|Verkauf"), "Amount"].sum()
        l_values.append(sum_i)
        l_taxes.append(
            i.loc[i["Description"].str.contains("gebühren"), "Amount"].sum())
        sum_q = 0
        for j in i.loc[i["Description"].str.contains("Kauf|Verkauf"), "Description"].values:
            if (any(w in j for w in word)):
                sum_q = sum_q + float(j.split()[2])
            else:
                sum_q = sum_q + float(j.split()[1])
        if ("Verkauf" in j):
            l_op.append("Vente")
            l_quantity.append(-sum_q)

        else:
            l_op.append("Achat")
            l_quantity.append(sum_q)

        l_prix.append(i.loc[i["Description"].str.contains(
            "Kauf|Verkauf"), "Description"].values[0].split()[4])
        l_currency.append(i.loc[i["Description"].str.contains(
            "Kauf|Verkauf"), "Currency"].values[0])

    table_deg = pd.DataFrame()
    table_deg["Date"] = l_date
    table_deg["Product"] = l_product
    table_deg["Description"] = l_op
    table_deg["Price"] = l_prix
    table_deg["Currency"] = l_currency
    table_deg["Quantity"] = l_quantity
    table_deg["Taxes"] = l_taxes
    table_deg["Amount"] = l_values
    table_deg["Total"] = table_deg["Amount"]+table_deg["Taxes"]
    # table_deg.sort_values(by="Date")

    ###################### Concat dividends and transactions ########################################

    table_transac = pd.concat([table_deg, table_for, table_div])
    # st.write(table_transac)
    table_transac["Date"] = pd.to_datetime(
        table_transac["Date"], infer_datetime_format=True, dayfirst=True)
    table_transac.sort_values(by="Date", inplace=True)
    # st.write(table_transac)

    ###################### Merge stock name & tickers name ########################################
    stock_histo = pd.read_csv("stock_final2")
    tracker_histo = pd.read_csv("tracker")
    tickers_list = pd.read_csv("data/product_tickers_currency.csv", sep=";")

    # st.write(tickers_list)
    ti_cu = tickers_list[["Product", "Tickers", "Currency"]]
    tickers_list = tickers_list[["Product", "Tickers"]]
    table_transac = table_transac.merge(tickers_list, on="Product", how="left")
    # if "Tickers" in table_transac.columns:
    #        table_transac.drop(columns=["Tickers"],inplace=True)

    ###################### Merge stock name & tickers name ########################################

    table_transac = pd.concat([table_transac, data])
    current_stock = table_transac[["Product", "Quantity"]].groupby(
        by="Product", as_index=False).sum(numeric_only=True)[table_transac[["Product", "Quantity"]].groupby(by="Product", as_index=False).sum()["Quantity"] > 0]
    # st.write('current_stock',current_stock)
    current_stock = current_stock.merge(ti_cu, on="Product", how="left")
    # st.write('current_stock', current_stock)
    current_stock = current_stock.groupby('Tickers').agg({
        'Quantity': 'sum',
        "Product": 'first',
        "Currency": 'first'
    }
    ).reset_index()

    # st.write('current_stock', current_stock)

# result = df.groupby('Group', as_index=False).agg({
#     'Value1': 'sum',
#     'Value2': 'sum',
#     'Description': 'first'  # Keeps the first occurrence of 'Description' in each group
# })
    # st.write(table_transac)
    table_transac["Date"] = pd.to_datetime(table_transac["Date"],format='ISO8601')
    table_transac.reset_index(inplace=True)
    table_transac.drop(columns=["index"], inplace=True)
    my_stocks = current_stock

    ######################## Import saving & concat with transac########################################################

    sav = pd.read_csv("data/saving")

    sav.replace(",", ".", inplace=True, regex=True)

    sav.fillna(0, inplace=True)

    ######################## Import stock values########################################################
    stop = timeit.default_timer()
    print("line 368 " + str(stop - start2))
    date_histo = stock_histo.Date.values[-5]
    stop = timeit.default_timer()
    stock_histo["Date"] = pd.to_datetime(stock_histo["Date"])

    # ajout le 24/11/22
    stock_histo.dropna(subset=["Close"], inplace=True)

    all = table_transac
    all.sort_values(by="Date", inplace=True)
    my_stocks.sort_values(by=["Tickers"], inplace=True)

    ##################### Export des transactions###################################
    # st.write(all)
    last_date = str(all[~(all["Description"].str.contains("Sto"))].sort_values(
        by="Date")["Date"].values[-1])[:10]
    all[~(all["Description"].str.contains("Sto"))].to_csv(last_date)
    ######################################### stock history#####################################
    last_date = all.Date.values[-1]
    first_date = all.Date.values[0]

    # ti_cu=ti_cu[["Tickers",	"Currency"]]
    # stock_final2=stock_final2[["Date","Close","Tickers","Currency"]]
    stock_final2 = stock_histo

    data = all[~(all["Description"].str.contains("Sto"))]

    data = data[["Date", "Description", "Quantity", "Total", "Tickers"]]
    tracker = tracker_histo[["Date", "Total", "Balance"]]
    last_d_tr = tracker.Date.values[-1]
    # last_d_tr="2016-10-10"
    data1 = data[data["Description"].str.contains("Achat|Vente")]

    day_end = (date.today()-date(pd.to_datetime(first_date).year,
               pd.to_datetime(first_date).month, pd.to_datetime(first_date).day)).days+1
    day_start = day_end-(date.today()-date(pd.to_datetime(last_d_tr).year,
                         pd.to_datetime(last_d_tr).month, pd.to_datetime(last_d_tr).day)).days-30  # à remettre sur 30
    # day_start=date(2016,10,1)
    # day_end=date(2022,10,9)

    for d in range(day_start, day_end, 1):
        # st.write(d)

        time_d = pd.to_datetime(first_date) + timedelta(days=d)
        # st.write(time_d)
        stock_final_d = stock_final2[(stock_final2["Date"] < (
            time_d+timedelta(days=1))) & (stock_final2["Date"] > (time_d - timedelta(days=10)))]
        stock_final_d = stock_final_d.drop_duplicates(
            subset=["Tickers"], keep="last")
        # test
        # stock_final_d.dropna(axis=0,inplace=True)
        # st.write(data1)

        table_transac = (data1[data1["Date"] < (time_d+timedelta(days=1))])[
            ["Tickers", "Quantity", "Total"]].groupby(by=["Tickers"]).sum(numeric_only=True).reset_index()
        table_transac = table_transac[table_transac["Quantity"] > 0]
        # st.write('stock_final_d',stock_final_d)
        # st.write(stock_final_d[(stock_final_d["Tickers"] ==
        #                         "GBpEUR=X")])
        # dict={}

        list_val = []
        list_val2 = []
        list_ch = []
        usd = stock_final_d[(stock_final_d["Tickers"] ==
                             "USDEUR=X")]["Close"].values[-1]
        try:
            gbp = stock_final_d[(stock_final_d["Tickers"]
                                 == "GBPEUR=X")]["Close"].values[-1]/100
        except:
            gbp = stock_final_d[(stock_final_d["Tickers"]
                                 == "GBpEUR=X")]["Close"].values[-1]/100

        sek = stock_final_d[(stock_final_d["Tickers"] ==
                             "SEKEUR=X")]["Close"].values[-1]
        pln = stock_final_d[(stock_final_d["Tickers"] ==
                             "PLNEUR=X")]["Close"].values[-1]
        # st.write(stock_final_d)
        for i in table_transac.Tickers.values:

            # st.write(table_transac)
            try:
                val = stock_final_d[(
                    stock_final_d["Tickers"] == i)]["Close"].values[-1]
                # st.write("val")
                # st.write(val)
                cur_val = stock_final_d[(
                    stock_final_d["Tickers"] == i)]["Currency"].values[-1]
                if (cur_val == "EUR"):
                    list_val.append(val)
                    list_val2.append(val)
                    list_ch.append(1.0)
                else:
                    if (cur_val == "USD"):
                        list_val.append(val*usd)
                        list_val2.append(val)
                        list_ch.append(usd)
                    else:
                        if (cur_val == "GBp"):
                            list_val.append(val*gbp)
                            list_val2.append(val)
                            list_ch.append(gbp)
                        else:
                            if (cur_val == "SEK"):
                                list_val.append(val*sek)
                                list_val2.append(val)
                                list_ch.append(sek)
                            else:
                                list_val.append(val*pln)
                                list_val2.append(val)
                                list_ch.append(pln)

            except IndexError:
                if (i == "IQQR.DE"):
                    list_val.append(4.7)
                    list_val2.append(4.7)
                    list_ch.append(1.0)

                else:
                    if ((i == "KN.PA") or (i == "MRW.L")):
                        list_val.append(data[(data["Description"] == "Vente") & (data["Tickers"] == i)]["Total"].values/abs(
                            data[(data["Description"] == "Vente") & (data["Tickers"] == i)]["Quantity"].values))
                        list_val2.append(data[(data["Description"] == "Vente") & (data["Tickers"] == i)]["Total"].values/abs(
                            data[(data["Description"] == "Vente") & (data["Tickers"] == i)]["Quantity"].values))
                        list_ch.append(1.0)
                    else:

                        list_val.append(
                            stock_final2[(stock_final2["Tickers"] == i)]["Close"].values[-1])
                        list_val2.append(
                            stock_final2[(stock_final2["Tickers"] == i)]["Close"].values[-1])
                        list_ch.append(1.0)

                        # stock_final_d

        table_transac["value_stock"] = [
            float(x) for x in list_val]*table_transac["Quantity"]

        res = ([float(x) for x in list_val]*table_transac["Quantity"]).sum() + \
            data[data["Date"] < (time_d+timedelta(days=1))]["Total"].sum()
        # st.write(res)
        # st.write("480")
        res2 = ([float(x) for x in list_val]*table_transac["Quantity"]).sum()
        table_transac["current_value"] = [
            float(x) for x in list_val]*table_transac["Quantity"]

        tracker = pd.concat([tracker, pd.DataFrame(
            [[time_d, res2, res]], columns=["Date", "Total", "Balance"])])
    # st.write("table_transac", table_transac)
    # st.write(list_val2)
    # st.write(len(list_val2))
    # st.write(list_ch)
    # st.write(len(list_ch))
    # st.write(my_stocks["Quantity"])
    # st.write('my_stocks', my_stocks)
    my_stocks["Values"], my_stocks["Change"] = list_val2, list_ch

    my_stocks["Total"] = my_stocks["Quantity"] * \
        my_stocks["Values"]*my_stocks["Change"]
    my_stocks["Date"] = datetime.today()
    my_stocks["Description"] = "Stock"
    all = pd.concat([all, my_stocks[["Product", "Quantity",
                    "Tickers", "Currency", "Total", "Date", "Description"]]])
    all.sort_values(by="Date", inplace=True)

    my_stocks.sort_values(by=["Tickers"], inplace=True)
    # st.write(my_stocks)

    tracker["Date"] = pd.to_datetime(tracker["Date"])
    tracker.drop_duplicates(subset=["Date"], inplace=True, keep="last")
    data_divi = pd.read_csv("data/dividend_list")
    tracker.to_csv("tracker")
    # stock_final2.to_csv("stock_final2")
    # all.to_csv("all")
    return ([all, stock_final2, tracker, sav, data_divi, my_stocks, tickers_list])


@st.cache_data
def sav_evolution(tr_sav1, tracker):

    tr_sav = tr_sav1.copy()
    tracker["Description"] = "Stock"
    tr_sav.dtypes
    tr_sav.loc[:, ["Date"]] = pd.to_datetime(tr_sav.loc[:, "Date"]).copy()
    tracker["Date"] = pd.to_datetime(tracker["Date"])
    tracker.dtypes
    data = pd.concat([tracker[["Date", "Total", "Description"]],
                     tr_sav[["Date", "Total", "Description"]]])
    data.sort_values(by="Date")

    list_date = []
    list_value = []
    from datetime import date

    d0 = date(2014, 3, 4)
    d1 = date.today()
    delta = d1 - d0
    # st.write(delta.days)
    for i in range(1, delta.days+1, 1):
        date_bal = (datetime(2014, 3, 4)+timedelta(days=i))
        bilan = data[data["Date"] <= date_bal]
        try:
            a = bilan[bilan["Description"] == "Stock"]["Total"].values[-1]
        except IndexError:
            a = 0
        sum_bilan = bilan[bilan["Description"] == "Saving"]["Total"].sum()+a
        list_date.append(date_bal)
        list_value.append(sum_bilan)
        # print(sum_bilan)
    data_bal = pd.DataFrame({"Date": list_date, "Valeur": list_value})
    return data_bal


@st.cache_data
def last_update(x):
    import os.path
    import time
    from os import listdir
    from os.path import isfile, join
    file_st = "stock_final2"
    a = ("Stocks quotes: %s" % time.ctime(os.path.getmtime(file_st)))
    file_div = "dividend_list"
    b = ("Distributed dividends: %s" %
         time.ctime(os.path.getmtime("data/" + file_div)))
    file_st = "saving"
    c = ("Savings: %s" % time.ctime(os.path.getmtime("data/" + file_st)))
    onlyfiles = [f for f in listdir(r"C:\Users\loicg\OneDrive\Documents\IT\banking\data") if isfile(
        join(r"C:\Users\loicg\OneDrive\Documents\IT\banking\data", f))]

    file_fo = sorted([x for x in onlyfiles if "FORTU" in x])[-1]

    d = ("Fortuneo: %s" % time.ctime(os.path.getmtime("data/" + file_fo)))
    file_de = sorted([x for x in onlyfiles if "DEGIRO" in x])[-1]

    e = ("Degiro: %s" % time.ctime(os.path.getmtime("data/" + file_de)))
    return (a, b, c, d, e)


@st.cache_data
def credit():
    import pandas as pd
    import datetime
    from datetime import timedelta
    from datetime import datetime
    from dateutil.relativedelta import relativedelta

    tableau = pd.DataFrame(
        columns=["date", "total_debt", "interest", "principal", 'property_value'])
    inter = 1.09
    rate = 645.96
    amount = 185000
    start = datetime(2020, 9, 1)

    remb = dict({
        datetime(2020, 10, 1): 9250,
        datetime(2021, 5, 1): 9250,
        datetime(2022, 8, 1): 9250,
        datetime(2023, 1, 1): 9250,
        datetime(2025, 6, 1): 7150,

    })

    date = [start]
    total_debt = [amount]
    interest = [151.24]
    principal = [430.12]
    monthly_payment = [rate]

    for i in range(1, 360, 1):
        # if((start+relativedelta(months=i))<=datetime.today()):
        if ((total_debt[-1] > 0)):

            date.append(start+relativedelta(months=i))
            total_debt.append(total_debt[-1]-(principal[-1]))
            interest.append(total_debt[-1]*inter/1200)
            if (date[-1] in remb.keys()):
                principal.append(remb[date[i]]+rate-interest[-1])
            else:
                principal.append(rate-interest[-1])
            monthly_payment.append(interest[-1]+principal[-1])

            if total_debt[-1] < 0:
                principal[-2] = interest[-2]+total_debt[-2]
                monthly_payment[-2] = interest[-2]+principal[-2]
                del date[-1]
                del total_debt[-1]
                del interest[-1]
                del principal[-1]
                del monthly_payment[-1]
    tableau["date"] = date
    tableau["total_debt"] = total_debt
    tableau["interest"] = interest
    tableau["principal"] = principal
    tableau["monthly_payment"] = monthly_payment
    tableau["property_value"] = 325000

    return tableau


@st.cache_data
def balance_all(tr_sav, tracker):
    import pandas as pd
    from datetime import date

    sav_int = tr_sav.copy()
    sav_int["Date"] = pd.to_datetime(sav_int["Date"])
    sav_int = sav_int[sav_int["Description"] == "Interest"][[
        "Date", "Total"]].sort_values(by="Date")
    sav_int = pd.concat([sav_int, pd.DataFrame(
        {"Date": [date.today()], "Total": [0]})])
    sav_int["Date"] = pd.to_datetime(sav_int["Date"])
    sav_int = sav_int.resample("D", on="Date").sum().reset_index()
    sav_int["cum_sum"] = sav_int["Total"].cumsum()
    bal = sav_int[["Date", "cum_sum"]].merge(
        tracker[["Date", "Balance"]], on="Date", how="left")
    bal.fillna(0, inplace=True)
    bal["balance"] = bal["Balance"]+bal["cum_sum"]
    return bal


@st.cache_data
def curve_saving(x, data_bal):
    # import streamlit as st
    # import plotly.express as px
    # import plotly.graph_objects as go
    # from plotly.subplots import make_subplots
    # import pandas as pd
    data_bal["date"] = data_bal["Date"]
    data_bal = data_bal[-x:]
    fig = make_subplots(specs=[[{"secondary_y": False}]])
    fig.add_trace(
        go.Scatter(x=data_bal.Date.values,
                   y=data_bal.Valeur.values, name="saving"),
        secondary_y=False,
    )
    fig.update_layout(
        title_text="Saving evolution",
        autosize=False,
        width=1200,
        height=400
    )
    fig.update_xaxes(title_text="Time")
    fig.update_yaxes(title_text="<b>Amount</b> €", secondary_y=False)
    return [fig, data_bal]
    # return st.plotly_chart(fig, use_container_width = True)


@st.cache_data
def curve_stock(x, tracker):
    tracker = tracker[-x:]

# Create figure with secondary y-axis
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    # Add traces
    fig.add_trace(
        go.Scatter(x=tracker.Date.values, y=tracker.Total.values,
                   name="portfolio value"),
        secondary_y=False,
    )
    fig.add_trace(
        go.Scatter(x=tracker.Date.values,
                   y=tracker.Balance.values, name="balance"),
        secondary_y=True,
    )
    # Add figure title
    fig.update_layout(
        title_text="Portfolio evolution",
        autosize=False,
        width=1200,
        height=400
    )
    fig.update_xaxes(title_text="Time")
    fig.update_yaxes(title_text="<b>Portfolio</b> €", secondary_y=False)
    fig.update_yaxes(title_text="<b>Balance</b> €", secondary_y=True)
    return [fig, tracker]


@st.cache_data
def curve_sav_debt(data_bal, credit, x):
    data_bal["date"] = data_bal["Date"]
    data_cred = credit[["date", "total_debt"]][-x:]
    data_cred.date = pd.to_datetime(data_cred.date)
    data_2 = data_bal.merge(data_cred, how="left")
    data_2["total_debt"].fillna(method="pad", inplace=True)
    data_2["debt + saving"] = -data_2["total_debt"][-x:]+data_2["Valeur"]
    data_2 = data_2[-x:]
    fig = make_subplots(specs=[[{"secondary_y": False}]])
    fig.add_trace(
        go.Scatter(x=data_2.date.values,
                   y=data_2["debt + saving"].values, name="debt + saving"),
        secondary_y=False,
    )
    fig.update_layout(
        title_text="Sum of debt & saving",
        autosize=False,
        width=1200,
        height=600
    )

    fig.update_xaxes(title_text="Time")
    fig.update_yaxes(title_text="<b>Amount</b> €", secondary_y=False)
    return [fig, data_2]


@st.cache_data
def pie_saving(my_stocks, data_divi, tr_sav, prop, size_x, size_y):
    current_stock_div = my_stocks.merge(data_divi, on="Product")
    # st.write(tr_sav.groupby("Product").sum())
    current_stock_div = pd.concat([pd.DataFrame({"Product": ["Stocks"], "Total": [
                                  current_stock_div.Total.sum()]}), tr_sav[["Product", "Total"]].groupby("Product").sum().reset_index()])
    if prop != 0:
        current_stock_div = pd.concat([pd.DataFrame(
            {"Product": ["Property assets"], "Total": [prop]}), current_stock_div])
    current_stock_div["% of portfolio"] = round(
        current_stock_div["Total"]/current_stock_div["Total"].values.sum()*100, 1)
    current_stock_div["Total"] = round(current_stock_div["Total"], 1)
    current_stock_div.reset_index(inplace=True, drop=True)
    current_stock_div.drop(
        current_stock_div[current_stock_div["Total"] < 11].index, inplace=True)
    current_stock_div["amount_k"] = current_stock_div["Total"].apply(
        lambda x: str((round(x/1000))) + " k€")
    current_stock_div["Product"] = current_stock_div["Product"] + \
        " - " + current_stock_div["amount_k"]
    current_stock_div.reset_index(inplace=True, drop=True)
    current_stock_div["Total"] = current_stock_div["Total"].astype(float)
    current_stock_div["% of portfolio"] = round(
        current_stock_div["Total"]/current_stock_div["Total"].sum()*100, 1)
    fig = px.pie(current_stock_div, values="% of portfolio",
                 names='Product', hover_data=['Total'])
    fig.update_traces(sort=False)
    # Add figure title
    fig.update_layout(
        # title_text="Savings overview",
        # autosize=False,
        width=size_x,
        height=size_y,
        annotations=[dict(text=("<b>€{}k</b>").format((int(round(current_stock_div.Total.sum()/1000)))),
                          x=0.5, y=0.5, font_size=60, showarrow=False)],
    )
    colours = ["#fbd206",
               "#feaf8a",
               "#fd7a8c",
               "#cc89d6",
               "#bfcff0",
               "#9ce7c9",
               "#4dc656",
               "#a6aab2"]
    fig.update_traces(textfont_size=120, hole=.4)
    fig.update_traces(textposition='inside', textinfo='percent+label', textfont_size=25,
                      marker=dict(line=dict(color='#000000', width=2),
                                  colors=colours
                                  ))
    fig.update(layout_showlegend=False)
    return [fig, current_stock_div]


@st.cache_data
def call_div_int(tr_sav: pd.DataFrame, my_stocks: pd.DataFrame, data_divi: pd.DataFrame) -> pd.DataFrame:
    current_stock_div = my_stocks.merge(data_divi, on="Product")
    current_stock_div["Dividends_net"] = current_stock_div["Dividends"] * \
        current_stock_div["Change"] * \
        current_stock_div["Quantity"]*current_stock_div["Net"]

    interest_table = pd.read_csv("data/interest")
    taux_la = (interest_table[interest_table["Product"] == "Livret A"]["Interest"].sum(
    ))*(interest_table[interest_table["Product"] == "Livret A"]["Net"].sum())/100
    taux_ING = (interest_table[interest_table["Product"] == "ING"]["Interest"].sum(
    ))*(interest_table[interest_table["Product"] == "ING"]["Net"].sum())/100
    taux_sb = (interest_table[interest_table["Product"] == "1_Sparbrief"]["Interest"].sum(
    ))*(interest_table[interest_table["Product"] == "1_Sparbrief"]["Net"].sum())/100
    taux_sb_2 = (interest_table[interest_table["Product"] == "2_Sparbrief"]["Interest"].sum(
    ))*(interest_table[interest_table["Product"] == "2_Sparbrief"]["Net"].sum())/100

    taux_lp = (interest_table[interest_table["Product"] == "Livret +"]["Interest"].sum())*(
        interest_table[interest_table["Product"] == "Livret +"]["Net"].sum())/100
    taux_wu = (interest_table[interest_table["Product"] == "1_Wüst."]["Interest"].sum(
    ))*(interest_table[interest_table["Product"] == "1_Wüst."]["Net"].sum())/100
    taux_wu_2 = (interest_table[interest_table["Product"] == "2_Wüst."]["Interest"].sum(
    ))*(interest_table[interest_table["Product"] == "2_Wüst."]["Net"].sum())/100
    taux_ka = (interest_table[interest_table["Product"] == "Livret Karl"]["Interest"].sum(
    ))*(interest_table[interest_table["Product"] == "Livret Karl"]["Net"].sum())/100

    invest = pd.DataFrame({
        "Product": ["Livret A", "1_Wüst.", "2_Wüst.", "ING", "Dividends", "Solar panel", "1_Sparbrief", "2_Sparbrief", "Livret +", "Livret Karl"],
        "Yearly income": [(tr_sav[tr_sav["Product"] == "Livret A"]["Total"].sum()*taux_la).round(1),
                          (tr_sav[tr_sav["Product"] == "1_Wüst."]
                          ["Total"].sum()*taux_wu),
                          (tr_sav[tr_sav["Product"] == "2_Wüst."]
                           ["Total"].sum()*taux_wu_2),

                          (tr_sav[tr_sav["Product"] == "ING"]
                           ["Total"].sum()*taux_ING),
                          current_stock_div["Dividends_net"].sum().round(1),
                          interest_table[interest_table["Product"]
                                         == "Solar panel"]["Net"].sum(),
                          (tr_sav[tr_sav["Product"] == "1_Sparbrief"]
                           ["Total"].sum()*taux_sb),
                          (tr_sav[tr_sav["Product"] == "2_Sparbrief"]
                           ["Total"].sum()*taux_sb_2),
                          (tr_sav[tr_sav["Product"] == "Livret +"]
                           ["Total"].sum()*taux_lp),
                          (tr_sav[tr_sav["Product"] == "Livret Karl"]
                           ["Total"].sum()*taux_ka).round(1)

                          ],
    })
    invest = pd.concat([invest, pd.DataFrame(
        {"Product": ["Total"], "Yearly income": [invest["Yearly income"].sum()]})])
    return invest


def float_to_euro(x):
    return f"{round(x,2):,.2f}".replace(","," ").replace(".",",")+" €"
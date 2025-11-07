import time
from PIL import Image
from bank_fct import balance_all
from os.path import isfile, join
from os import listdir
from bank_fct import call_div_int
from bank_fct import pie_saving
from bank_fct import curve_sav_debt
from bank_fct import curve_stock
from bank_fct import curve_saving
from bank_fct import credit
from bank_fct import last_update
from bank_fct import sav_evolution
from bank_fct import vroumvroum
from bank_fct import float_to_euro


import timeit
from dateutil.relativedelta import relativedelta
from datetime import timedelta, date
from datetime import datetime
from st_aggrid import AgGrid, GridOptionsBuilder, ColumnsAutoSizeMode
from streamlit_plotly_events import plotly_events
import xlsxwriter
# import datetime
import matplotlib.pyplot as plt
import math
import copy
from random import randint
from random import randrange
import pandas as pd
import numpy as np
import seaborn as sns
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st
from turtle import width
from tabnanny import check
from re import sub
import io
import os

import sys


os.chdir(r"C:\Users\loicg\OneDrive\Documents\IT\banking")
st.set_page_config(layout="wide",
                   page_title="Finance",
                   page_icon="img/pig.png"
                   )


# import seaborn.objects as so

# pd.options.display.max_columns = None
# pd.options.display.max_rows = 100


# def do_stuff_on_page_load():
# st.set_page_config(layout="wide",
#                     page_title="Finance",
#                     page_icon="img/pig.png"
#                     )

# do_stuff_on_page_load()
st.write(sys.version)
st.write(st.__version__)
# st.write(os.environ)
st.markdown("""
  <style>
    .css-1vq4p4l {
      padding-top: 1em;
    }
  </style>
""", unsafe_allow_html=True)
start = timeit.default_timer()
if 'stock_update' not in st.session_state:
    st.session_state['stock_update'] = os.path.getmtime("stock_final2")

a, b, c, d, e = last_update(st.session_state["stock_update"])
stop = timeit.default_timer()
st.write('Time_79: ', stop - start)
st.session_state["stock_update"] = os.path.getmtime("stock_final2")
stop = timeit.default_timer()
st.write('Time_80: ', stop - start)
all, stock_final2, tracker, tr_sav1, data_divi, my_stocks, t_list = vroumvroum(
    st.session_state["stock_update"])
tr_sav = tr_sav1[tr_sav1["Description"] == "Saving"]
# st.write(tr_sav)
# st.write(tracker)
# st.write(tracker.Total)

data_bal = sav_evolution(tr_sav, tracker)

r = balance_all(tr_sav1, tracker)

credit_1 = credit()
credit_1 = credit_1[credit_1["date"] <= datetime.today()]

stop = timeit.default_timer()
st.write('Time_95: ', stop - start)
# st.dataframe(credit)
m = st.markdown("""
<style>
div.stButton > button:first-child {
    # background-color: #ce1126;
    # color: white;
    height: 40px;
    width: 200px;
    border-radius:15px;
    border:3px solid #000000;
    font-size:20px;
    font-weight: bold;
    margin: auto;
    display: block;
}

# div.stButton > button:hover {
# 	background:linear-gradient(to bottom, #ce1126 5%, #ff5a5a 100%);
# 	background-color:#ce1126;
# }

# div.stButton > button:active {
# 	position:relative;
# 	top:3px;
# }

</style>""", unsafe_allow_html=True)

hide_dataframe_row_index = """
            <style>
            .row_heading.level0 {display:none}
            .blank {display:none}
            </style>
            """
# left_co, cent_co,last_co = st.columns(3)
# with cent_co:
#     # st.image(logo)
#     st.sidebar.image("img/savings.png")
with st.sidebar:
    left_co, cent_co, last_co = st.columns([1, 2, 1])
    # with left_co:
    #     st.image("img/savings.png")
    with cent_co:
        if st.button("Update stocks"):
            exec(open("stock_update.py").read())
            # exec(st.experimental_rerun())
            st.session_state["stock_update"] = os.path.getmtime("stock_final2")
            a, b, c, d, e = last_update(st.session_state["stock_update"])
    # with last_co:
    #     st.image("img/savings_gespiegelt.png")
st.sidebar.subheader('Last update:')

st.sidebar.markdown('<p class="big-font">{}</br>{}</br>{}</br>{}</br>{}</p>'.format(a,
                    b, c, d, e), unsafe_allow_html=True)
# buffer to use for excel writer
buffer = io.BytesIO()

# download button 2 to download dataframe as xlsx
if st.sidebar.checkbox("Prepare XLSX export?"):
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        # Write each dataframe to a different worksheet.
        all.to_excel(writer, sheet_name='all', index=False)
        stock_final2.to_excel(writer, sheet_name='stock_final2', index=False)
        tracker.to_excel(writer, sheet_name='tracker', index=False)
        tr_sav1.to_excel(writer, sheet_name='tr_sav1', index=False)
        data_divi.to_excel(writer, sheet_name='data_divi', index=False)
        my_stocks.to_excel(writer, sheet_name='my_stocks', index=False)
        t_list.to_excel(writer, sheet_name='t_list', index=False)
        data_bal.to_excel(writer, sheet_name='data_bal', index=False)
        credit_1.to_excel(writer, sheet_name='credit_1', index=False)
        writer.save()
        download2 = st.sidebar.download_button(
            label="Download data as Excel",
            data=buffer,
            file_name='finance_data.xlsx',
            mime='application/vnd.ms-excel'
        )

col1, col2, col3 = st.columns((1, 5, 1))
# col1.image("img/savings.png", use_column_width=True)
# col2.markdown("<h1 style='text-align: center; white: red;font-size: 60px;'> OVERVIEW OF ASSETS </h1>", unsafe_allow_html=True)
# col3.image("img/savings_gespiegelt.png", use_column_width=True)

st.markdown("""
<style>
.big-font {
    font-size: 12px;
}
</style>
""", unsafe_allow_html=True)

all2 = all[~(all["Description"].str.contains("Sto"))]
st.sidebar.subheader('Dashboard')
aujourdhui = pd.to_datetime(all.Date.values[-1])
aujourdhui = datetime(aujourdhui.year, aujourdhui.month, aujourdhui.day)
# stop = timeit.default_timer()
# st.write('Time: ', stop - start)
if st.sidebar.checkbox("My dashboard", True):
    start = timeit.default_timer()

    col1, col2 = st.columns((1, 1))
    col3, col4 = st.columns((1, 1))
    # col3,col4,col5=st.columns((1,5,1))
    # col6,col7,col8=st.columns((1,5,1))

    with col1:
        st.plotly_chart(curve_saving(200, data_bal)[
                        0], use_container_width=True)

    with col2:
        st.plotly_chart(curve_stock(200, tracker)[0], use_container_width=True)

    with col4:
        st.plotly_chart(curve_sav_debt(data_bal, credit_1, 200)
                        [0], use_container_width=True)

    with col3:
        st.markdown("**Assets overview**")
        sav_d_3 = curve_sav_debt(data_bal, credit_1, 10000)[1]
        tempo_6538 = sav_d_3.loc[(sav_d_3.index)[-1:]]
        p_a = 325000-tempo_6538.total_debt.values[0]
        on = st.toggle("with property assets")
        if on == 0:
            p_a = 0
        st.plotly_chart(pie_saving(my_stocks, data_divi, tr_sav, p_a, 600, 600)[
                        0], use_container_width=True)

    st.markdown("**Table year over year**")
    sav_d_1 = curve_saving(10000, data_bal)[1].copy()
    sav_d_1.loc[:, "Date_2"] = sav_d_1.loc[:, "Date"].apply(
        lambda x: str(x.strftime("%m%d")))
    tempo_6536 = (pd.DataFrame(sav_d_1.loc[(sav_d_1.index)[-1:]]))
    sav_d_1 = pd.concat(
        [tempo_6536, sav_d_1[sav_d_1["Date_2"] == "1231"]]).sort_values(by="Date")
    sav_d_1 = (sav_d_1
               .rename(columns={"Valeur": "total_saving", "Date": "date_1"})
               .drop(axis=1, columns=["Date_2", "date_1"])
               ).reset_index()
    sav_d_1["gap_saving"] = 0
    for i in range(1, len(sav_d_1.index)):
        sav_d_1.loc[i, 'gap_saving'] = sav_d_1.loc[i,
                                                   'total_saving'] - sav_d_1.loc[i-1, 'total_saving']
    sav_d_1 = sav_d_1.set_index("date").drop(axis=1, columns=["index"])

    sav_d_2 = curve_stock(10000, tracker)[1].reset_index()
    sav_d_2["Date_2"] = sav_d_2["Date"].apply(
        lambda x: str(x.strftime("%m%d")))
    tempo_6537 = (pd.DataFrame(sav_d_2.loc[(sav_d_2.index)[-1:]]))
    sav_d_2 = pd.concat(
        [tempo_6537, sav_d_2[sav_d_2["Date_2"] == "1231"]]).sort_values(by="Date")
    sav_d_2 = (sav_d_2
               .rename(columns={"Total": "total_stock", "Balance": "balance", "Date": "date"})
               .drop(axis=1, columns=["Date_2", "index", "balance"])
               ).reset_index()
    for i in range(1, len(sav_d_2.index)):
        sav_d_2.loc[i, 'gap_stock'] = sav_d_2.loc[i,
                                                  'total_stock'] - sav_d_2.loc[i-1, 'total_stock']
    sav_d_2 = sav_d_2.set_index("date").drop(axis=1, columns=["index"])
    sav_d_2 = sav_d_2[["total_stock", "gap_stock"]]

    sav_d_3 = curve_sav_debt(data_bal, credit_1, 10000)[1]
    sav_d_3["Date_2"] = sav_d_3["Date"].apply(
        lambda x: str(x.strftime("%m%d")))
    sav_d_3["total_debt"] = sav_d_3["total_debt"]*(-1)
    tempo_6538 = (pd.DataFrame(sav_d_3.loc[(sav_d_3.index)[-1:]]))

    sav_d_3 = pd.concat(
        [tempo_6538, sav_d_3[sav_d_3["Date_2"] == "1231"]]).sort_values(by="Date")

    sav_d_3 = (sav_d_3
               .rename(columns={"Valeur": "valeur"})
               .drop(axis=1, columns=["Date_2", "Date"])
               ).reset_index()

    for i in range(1, len(sav_d_3.index)):
        sav_d_3.loc[i, 'gap_debt'] = sav_d_3.loc[i,
                                                 'total_debt'] - sav_d_3.loc[i-1, 'total_debt']
        if (sav_d_3.date[i].year) == 2020:
            sav_d_3.loc[i, "gap_debt"] = 185000 + sav_d_3.loc[i, "total_debt"]

    # sav_d_3.loc[0,"gap_debt"] = 185000 + sav_d_3.loc[0,"total_debt"]

    sav_d_3 = sav_d_3.set_index("date").drop(axis=1, columns=["index"])
    for i in range(1, len(sav_d_3.index)):
        if (sav_d_3.index[i].year) >= 2020:
            sav_d_3.loc[sav_d_3.index[i], "property"] = 325000

    all_sav = sav_d_1.join(sav_d_2).join(sav_d_3)
    all_sav.fillna(0, inplace=True)
    all_sav.drop(columns="valeur", axis=1, inplace=True)
    all_sav["debt + saving"] = all_sav["total_debt"]+all_sav["total_saving"]
    all_sav["debt + sav + property"] = all_sav["total_debt"] + \
        all_sav["total_saving"]+all_sav["property"]
    all_sav['gap_debt + sav + property'] = 0

    for i in range(1, len(all_sav.index), 1):
        all_sav.iloc[i, 9] = all_sav.iloc[i, 8] - all_sav.iloc[i-1, 8]

    c1, c2, c3 = st.columns([1, 10, 1])
    # c2.write(all_sav)
    t_da = all_sav.copy()
    # t_da[['total_saving','gap_saving']] = t_da[['total_saving','gap_saving']].applymap(lambda x: float_to_euro(x))
    
    with c2:
        
        columns_to_format = ["total_saving", "gap_saving", "total_stock","gap_stock","total_debt", "gap_debt", "property", "debt + saving", "debt + sav + property", "gap_debt + sav + property"]
        column_config = {
            col: st.column_config.NumberColumn(
                col.replace("_", " ").title(),
                format="euro"
            ) for col in columns_to_format
        }
        st.dataframe(t_da,
                    height=(len(t_da.index) + 1) * 35 + 12,
                    use_container_width=True,
                    column_config=column_config

        #     column_config={
        #         "total_saving": st.column_config.NumberColumn(
        #             "Total saving",
        #             help="Saving, ETF, stocks, etc.",

        #             format="euro"
        #         )
        # },                 
                    )    
    
    
    # with c2:
    #     st.dataframe(all_sav,
    #                 height=(len(all_sav.index) + 1) * 35 + 12,
    #                 use_container_width=True,
    #         column_config={
    #             "total_saving": st.column_config.NumberColumn(
    #                 "Total saving",
    #                 help="Saving, ETF, stocks, etc.",

    #                 format="euro".replace("." , " "),
    #             )
    #     },                 
    #                 )
    stop = timeit.default_timer()
    # st.write('Time: ', stop - start)

st.sidebar.subheader('Data')
if 'p' not in st.session_state:
    st.session_state['p'] = ["ORANGE"]
if 'o' not in st.session_state:
    st.session_state['o'] = ["Achat"]


if st.sidebar.checkbox("Transactions list", False):

    # if st.button("TEST_1"):
    #     p1=["ORANGE"]
    #     o1=["Achat"]
    # if st.button("TEST_2"):
    #     p1=["WELLTOWER INC. COMMON"]
    #     o1=["Vente"]

    time_range = st.slider(
        'Select a range of time',
        min_value=datetime(2016, 9, 1), max_value=aujourdhui+timedelta(days=1), value=(datetime(2016, 9, 1), aujourdhui))
    # options = st.multiselect("Choose a stock:", all.Product.unique())
    options = st.multiselect("Choose a stock:", all.Product.unique(), key="p")
    if len(options) == 0:
        options = all.Product.unique()
        # options=p1
    # options2 = st.multiselect("Choose an operation:", all.Description.unique())
    options2 = st.multiselect("Choose an operation:",
                              all.Description.unique(), key="o")

    if len(options2) == 0:
        options2 = all.Description.unique()
        # options=o1
    transac_opt = all[(all["Product"].isin(options)) & (all["Description"].isin(
        options2)) & (all["Date"] >= time_range[0]) & (all["Date"] <= time_range[1])]
    transac_opt = transac_opt.sort_values(by="Date", ascending=False)
    st.dataframe(transac_opt, use_container_width=True)
    # AgGrid(transac_opt,columns_auto_size_mode=ColumnsAutoSizeMode.FIT_ALL_COLUMNS_TO_VIEW)
    st.write("Sum of the total column: {} €".format(
        transac_opt.Total.sum().round(1)))

if st.sidebar.checkbox("Stocks value per day", False):
    s_v_0 = my_stocks[["Product", "Tickers", "Currency"]]
    # stock_name=pd.read_csv("")
    stock_values = stock_final2[["Date", "Close", "Tickers", "Currency"]].merge(
        right=t_list, on="Tickers")

    d_0 = datetime.today()
    # d_1 = datetime(year=d_2.year-1, month=12, day=31)
    # d_2 = datetime.today()
    d_1 = datetime.today() + timedelta(days=-1)
    d_7 = datetime.today() + timedelta(days=-7)
    d_30 = datetime.today() + timedelta(days=-30)
    d_182 = datetime.today() + timedelta(days=-182)
    d_365 = datetime.today() + timedelta(days=-365)
    # st.write(d_30)
    # st.write(d_2)
    list_name_dates = ["0", "-1", "-7", "-30", "-182", "-365"]
    list_dates = [d_0, d_1, d_7, d_30, d_182, d_365]
    stock_values = stock_values.sort_values(by="Date", ascending=False)
    # s_v_0 = stock_values[stock_values["Date"]<=d_0].drop_duplicates(subset=["Tickers"])
    # s_v_0.rename(columns={"Date": "d_0","Close":"Close_d_0"},inplace=True)
    # s_v_0.drop(axis=1,labels=["Product","Currency"],inplace=True)

    for i in range(0, len(list_dates), 1):
        s_v_1 = stock_values[stock_values["Date"] <=
                             list_dates[i]].drop_duplicates(subset=["Tickers"])
        s_v_1.drop(axis=1, labels=["Product",
                   "Currency", "Date"], inplace=True)
        # "Date": list_name_dates[i],
        s_v_1.rename(columns={"Close": "Close_" +
                     list_name_dates[i]}, inplace=True)
        # s_v_1.drop(axis=1,labels=["Product","Currency"],inplace=True)
        # st.write(s_v_1)
        s_v_0 = pd.merge(left=s_v_0, right=s_v_1, on=["Tickers"])
        s_v_0["p" + list_name_dates[i]
              ] = (-s_v_0["Close_"+list_name_dates[i]] + s_v_0["Close_0"])/(s_v_0["Close_0"])

    cols_l1 = st.columns(5)
    # cols_l1[compt].subheader(i[1:]+'-Day Change')
    # cols_l2=st.columns(8)
    tc = 0
    for i in ["-1", "-7", "-30", "-182", "-365"]:
        cols_l1[tc].subheader(i[1:]+'-Day Change')
        tc = tc+1
    for z in range(1, len(s_v_0.index), 1):
        compt = 0
        for i in ["-1", "-7", "-30", "-182", "-365"]:
            xc = s_v_0.sort_values(
                by="p"+i)[["Product", "p"+i, "Close_"+i, "Close_0"]]
            cols_l1[compt].metric(label=xc.iloc[z]["Product"], value=str(round(
                xc.iloc[z]["p"+i]*100, 2)) + "%", delta=round(-xc.iloc[z]["Close_"+i]+xc.iloc[z]["Close_0"], 3))
            compt = compt+1

    # st.dataframe(stock_values,use_container_width=True,height=850)
    MIN_HEIGHT = 27
    MAX_HEIGHT = 350
    ROW_HEIGHT = 35
    # AgGrid(stock_values,columns_auto_size_mode=ColumnsAutoSizeMode.FIT_ALL_COLUMNS_TO_VIEW,height=min(MIN_HEIGHT + len(stock_values) * ROW_HEIGHT, MAX_HEIGHT),)
    l_stocks = st.multiselect(
        "Choose the stocks to display:", stock_values.Product.unique(), ["ORANGE"])
    d_stocks = stock_values[stock_values["Product"].isin(l_stocks)]
    fig = px.line(d_stocks, x=d_stocks["Date"],
                  y=d_stocks["Close"], color="Product")
    st.plotly_chart(fig, use_container_width=True)
if st.sidebar.checkbox("Balance", False):
    st.dataframe(tracker, use_container_width=True, height=850)

if st.sidebar.checkbox("Savings list", False):
    tr_sav1.Date = pd.to_datetime(tr_sav1.Date)
    time_range = st.slider(
        'Select a range of time',
        min_value=datetime(2014, 1, 1), max_value=aujourdhui, value=(datetime(2014, 1, 1), aujourdhui))
    options = st.multiselect("Choose a bank account:",
                             tr_sav1.Product.unique())
    if len(options) == 0:
        options = tr_sav1.Product.unique()
    options2 = st.multiselect("Choose an operation:",
                              tr_sav1.Description.unique())
    if len(options2) == 0:
        options2 = tr_sav1.Description.unique()
    transac_opt = tr_sav1[(tr_sav1["Product"].isin(options)) & (tr_sav1["Description"].isin(
        options2)) & (tr_sav1["Date"] >= time_range[0]) & (tr_sav1["Date"] <= time_range[1])]
    transac_opt["Date"] = transac_opt["Date"].apply(
        lambda x: x.strftime("%Y-%m-%d"))
    transac_opt = transac_opt.set_index('Date')
    sum_tot = transac_opt.Total.sum().round(1)
    transac_opt = transac_opt.style.format(
        subset=["Total"], formatter="{:.2f}",)

    st.dataframe(transac_opt, use_container_width=True)

    st.write("Sum of the total column: {} €".format(sum_tot))
    # st.dataframe(tr_sav1,use_container_width=True,height=850)

if st.sidebar.checkbox('Estimated dividends & interests', False):

    # define function to sum div. & int.
    # def call_div_int(tr_sav :pd.DataFrame, my_stocks:pd.DataFrame,data_divi:pd.DataFrame) -> pd.DataFrame:
    #     current_stock_div=my_stocks.merge(data_divi,on="Product")
    #     current_stock_div["Dividends_net"]=current_stock_div["Dividends"]*current_stock_div["Change"]*current_stock_div["Quantity"]*current_stock_div["Net"]

    #     interest_table=pd.read_csv("data/interest")
    #     taux_la=(interest_table[interest_table["Product"]=="Livret A"]["Interest"].sum())*(interest_table[interest_table["Product"]=="Livret A"]["Net"].sum())/100
    #     taux_ING=(interest_table[interest_table["Product"]=="ING"]["Interest"].sum())*(interest_table[interest_table["Product"]=="ING"]["Net"].sum())/100
    #     taux_sb=(interest_table[interest_table["Product"]=="Sparbrief"]["Interest"].sum())*(interest_table[interest_table["Product"]=="Sparbrief"]["Net"].sum())/100
    #     taux_lp=(interest_table[interest_table["Product"]=="Livret +"]["Interest"].sum())*(interest_table[interest_table["Product"]=="Livret +"]["Net"].sum())/100

    #     invest=pd.DataFrame({
    #         "Product":["Livret A","Wüst.","ING","Dividends","Solar panel","Sparbrief","Livret +"],
    #         "Yearly income":[(tr_sav[tr_sav["Product"]=="Livret A"]["Total"].sum()*taux_la).round(1),
    #             (tr_sav[tr_sav["Product"]=="Wüst."]["Total"].sum()*0.002),
    #             (tr_sav[tr_sav["Product"]=="ING"]["Total"].sum()*taux_ING),
    #             current_stock_div["Dividends_net"].sum().round(1),
    #             1260,
    #             (tr_sav[tr_sav["Product"]=="Sparbrief"]["Total"].sum()*taux_sb),
    #             (tr_sav[tr_sav["Product"]=="Livret +"]["Total"].sum()*taux_lp)

    #             ],
    #         })
    #     invest = pd.concat([invest, pd.DataFrame({"Product":["Total"],"Yearly income":[invest["Yearly income"].sum()]})])
    #     return current_stock_div,invest

    st.subheader('Estimated dividend per stock')
    c1, c3, c2 = st.columns((1, 1, 1))
    with c1:
        opt_1 = st.radio("Sort table by:", ("Yield", "Dividends net"))
        if opt_1 == "Dividends net":
            sort_opt = "Dividends_net"
            color_opt = "Div_net"
        else:
            sort_opt = "yield"
            color_opt = "yield"

    with c3:
        opt_3 = c3.radio("Style table", ("coolwarm", "binary", "viridis"))
    with c2:
        opt_2 = c2.radio("Filter", ("none", "EUR", "USD", "GBp", "ETF"))

    current_stock_div = my_stocks.merge(data_divi, on="Product")
    if opt_2 != "none":
        if opt_2 == "ETF":
            current_stock_div = current_stock_div[current_stock_div["Product"].str.contains(
                "ISHAR|IS EUR|ISHR UK")]
        if opt_2 == "EUR":
            current_stock_div = current_stock_div[~(
                current_stock_div["Product"].str.contains("ISHAR|IS EUR|ISHR UK"))]
            current_stock_div = current_stock_div[current_stock_div["Currency"] == opt_2]
        if (opt_2 != "EUR") & (opt_2 != "ETF"):
            current_stock_div = current_stock_div[~(
                current_stock_div["Product"].str.contains("ISHAR|IS EUR|ISHR UK"))]

            current_stock_div = current_stock_div[current_stock_div["Currency"] == opt_2]

    current_stock_div["Dividends_net"] = current_stock_div["Dividends"] * \
        current_stock_div["Change"] * \
        current_stock_div["Quantity"]*current_stock_div["Net"]
    current_stock_div["yield"] = round(
        current_stock_div["Dividends_net"]/current_stock_div["Total"]*100, 1)
    tot_div = current_stock_div.copy()
    current_stock_div.sort_values(by=sort_opt, ascending=False, inplace=True)

    current_stock_div.rename(columns={
                             "Currency": "Cur.", 'Dividends_net': 'Div_net', 'Dividends': 'Div.'}, inplace=True)
    current_stock_div.drop(columns=["Description"], inplace=True)
    current_stock_div["Product"] = current_stock_div["Product"].apply(
        lambda x: x[0:20])
    current_stock_div["Date"] = current_stock_div["Date"].apply(
        lambda x: x.strftime("%y-%m-%d"))

    st.table(current_stock_div.style
             .format(subset=['Div_net', "yield", "Change", 'Div.', 'Net', 'Total', 'Values'], formatter="{:.2f}",)
             .format(subset=["Quantity"], formatter="{:.0f}",)
             .background_gradient(axis=0, gmap=current_stock_div[color_opt],
                                  cmap=opt_3
                                  ))

    st.subheader('')
    st.divider()
    st.subheader('Estimated dividends - Group')

    opt_2 = st.radio("Group & sum the table by:", ("Currency", "Region"))
    if opt_2 == "Currency":
        current_stock_div = my_stocks.merge(data_divi, on="Product")
        current_stock_div["Dividends_net"] = current_stock_div["Dividends"] * \
            current_stock_div["Change"] * \
            current_stock_div["Quantity"]*current_stock_div["Net"]
        current_stock_div = current_stock_div.groupby(
            ["Currency"],).sum(numeric_only=True)
        current_stock_div["Percent"] = current_stock_div["Dividends_net"] / \
            current_stock_div["Dividends_net"].sum()*100
        current_stock_div["Currency"] = current_stock_div.index
        current_stock_div = current_stock_div[[
            "Currency", "Total", "Dividends_net", "Percent"]]
        current_stock_div = current_stock_div.style.format(subset=['Percent'], formatter="{:.2f}%",).format(
            subset=["Total", "Dividends_net"], formatter="{:.2f}",)

        st.table(current_stock_div)
        # st.table(current_stock_div[["Currency","Total","Dividends_net","Percent"]])
    else:
        st.write("Not available")

    st.divider()
    st.subheader('Sum of estimated dividends & interest')

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
    taux_wu_3 = (interest_table[interest_table["Product"] == "3_Wüst."]["Interest"].sum(
    ))*(interest_table[interest_table["Product"] == "3_Wüst."]["Net"].sum())/100
    taux_ka = (interest_table[interest_table["Product"] == "Livret Karl"]["Interest"].sum(
    ))*(interest_table[interest_table["Product"] == "Livret Karl"]["Net"].sum())/100

    # invest = pd.DataFrame({
    #     "Product": ["Livret A", "1_Wüst.", "2_Wüst.","3_Wüst.", "ING", "Dividends", "Solar panel", "1_Sparbrief", "2_Sparbrief", "Livret +", "Livret Karl"],
    #     "Yearly income": [(tr_sav[tr_sav["Product"] == "Livret A"]["Total"].sum()*taux_la).round(1),
    #                       (tr_sav[tr_sav["Product"] == "1_Wüst."]
    #                       ["Total"].sum()*taux_wu),
    #                       (tr_sav[tr_sav["Product"] == "2_Wüst."]
    #                        ["Total"].sum()*taux_wu_2),
    #                       (tr_sav[tr_sav["Product"] == "3_Wüst."]
    #                        ["Total"].sum()*taux_wu_3),

    #                       (tr_sav[tr_sav["Product"] == "ING"]
    #                        ["Total"].sum()*taux_ING),
    #                       tot_div["Dividends_net"].sum().round(1),
    #                       interest_table[interest_table["Product"]
    #                                      == "Solar panel"]["Interest"].sum(),
    #                       (tr_sav[tr_sav["Product"] == "1_Sparbrief"]
    #                        ["Total"].sum()*taux_sb),
    #                       (tr_sav[tr_sav["Product"] == "2_Sparbrief"]
    #                        ["Total"].sum()*taux_sb_2),
    #                       (tr_sav[tr_sav["Product"] == "Livret +"]
    #                        ["Total"].sum()*taux_lp),
    #                       (tr_sav[tr_sav["Product"] == "Livret Karl"]
    #                        ["Total"].sum()*taux_la).round(1)

    #                       ],
    # })

    my_invest = pd.merge(left=tr_sav.groupby(by=["Product"]).sum(numeric_only=True
                                                                 ), right=interest_table, how='outer', on="Product")
    my_invest = my_invest.loc[~my_invest["Net"].isna()]
    my_invest["Total"] = my_invest["Total"].fillna(1)

    my_invest["Yearly_income"] = my_invest["Total"] * \
        my_invest["Interest"]*my_invest["Net"]
    my_invest = pd.concat([
        my_invest,
        pd.DataFrame({
            "Product": ["Dividends"],
            'Total': [my_stocks.merge(data_divi, on="Product").Total.sum()],
            "Yearly_income": [
                tot_div["Dividends_net"].sum().round(1)],
            'Interest': [tot_div["Dividends_net"].sum()/my_stocks.merge(data_divi, on="Product").Total.sum()],
            'Net': [1]
        })
    ])
    my_invest["Monthly_income"] = my_invest["Yearly_income"]/12

    # my_invest = pd.concat([my_invest, pd.DataFrame(
    #     {"Product": ["Total"], "Yearly_income": [my_invest["Yearly_income"].sum()]})])
    my_invest["Monthly_income"] = my_invest["Yearly_income"]/12
    my_invest = my_invest.reset_index(drop=True)
    my_invest = my_invest.sort_values(by='Yearly_income', ascending=False)
    # def magnify():
    #     return [dict(selector="th",
    #                  props=[("font-size", "15pt")]),
    #             dict(selector="td",
    #                  props=[('padding', "0em 0em")]),
    #             dict(selector="th:hover",
    #                  props=[("font-size", "12pt")]),
    #             # dict(selector="tr:hover td:hover",
    #             dict(selector="tr:hover",
    #                  props=[('max-width', '200px'),
    #                         ('font-size', '20pt')])
    #             ]

    # .set_na_rep(" ")\
    st.markdown(hide_dataframe_row_index, unsafe_allow_html=True)
    my_invest = my_invest[my_invest['Yearly_income'] > 0.001]
    my_invest.loc[my_invest['Product'] == "Solar panel", "Total"] = np.nan
    my_invest.loc[my_invest['Product'] == "Solar panel", "Interest"] = np.nan
    len_my_invest = len(my_invest)
    # st.write(my_invest)
    my_invest_t = my_invest\
        .style\
        .background_gradient(axis=0, gmap=my_invest['Yearly_income'], cmap=opt_3)\
        .format(subset=['Monthly_income', 'Yearly_income'], formatter="{:,.2f} €")\
        .format(subset=['Total'], na_rep=' ', formatter="{:,.2f} €")\
        .format(subset=['Net'], formatter="{:.0%}")\
        .format(subset=['Interest'], formatter="{:.2%}", na_rep=' ')\
        # .apply(lambda x: ['font-weight: bold' if x.name in [len_my_invest-1] else '' for i in x], axis=1)\

    # st.write(my_invest['Total'])
    # .set_table_styles(magnify())
    # my_invest['Net'] = my_invest['Net'].apply(lambda x: x*10000000)
    # st.write(my_invest["Product"].apply(lambda x: x.replace("nan", "")))
    # st.write(my_invest["Total"].sum())
    st.table(my_invest_t)
    st.markdown(hide_dataframe_row_index, unsafe_allow_html=True)

    gau, mil, dro = st.columns(3)
    with gau:
        st.metric(value=f'{my_invest.Total.sum().round(0):,.0f} €'.replace(",", " "),
                  label="Amount invested")
    with mil:
        st.metric(value=f'{my_invest.Yearly_income.sum().round(0):,.0f} €'.replace(",", " "),
                  label="Yearly income")
    with dro:
        st.metric(value=f'{((my_invest.Yearly_income.sum())/12).round(0):,.0f} €'.replace(",", " "),
                  label="Monthly income")

    # st.write(my_invest)

    # invest = pd.concat([invest, pd.DataFrame(
    #     {"Product": ["Total"], "Yearly income": [invest["Yearly income"].sum()]})])
    # invest["Monthly income"] = invest["Yearly income"]/12

    # invest = invest.reset_index(drop=True).style.format(subset=['Monthly income', "Yearly income"], formatter="€{:.2f}").apply(lambda x: ['font-weight: bold' if x.name in [10]
    #                                                                                                                                       else '' for i in x],
    #                                                                                                                            axis=1)

    # st.table(invest)
    # st.markdown(hide_dataframe_row_index, unsafe_allow_html=True)

    # st.dataframe(all[(all["Description"].isin(["Dividend"]))&(all["Date"]>=(datetime.today()+timedelta(days=-365)))].groupby(["Product"]).sum()[["Total"]])
    div_400 = all[(all["Description"].isin(["Dividend"])) & (all["Date"] >= (
        datetime.today()+timedelta(days=-365)))].groupby(["Product"]).sum(numeric_only=True)[["Total"]]
    div_400.rename(columns={"Total": "Paid dividends"}, inplace=True)
    current_stock_div = my_stocks.merge(data_divi, on="Product")
    current_stock_div["Dividends_net"] = current_stock_div["Dividends"] * \
        current_stock_div["Change"] * \
        current_stock_div["Quantity"]*current_stock_div["Net"]
    current_stock_div["yield"] = round(
        current_stock_div["Dividends_net"]/current_stock_div["Total"]*100, 1)

    current_stock_div.rename(columns={
                             "Currency": "Cur.", 'Dividends_net': 'Estimation', 'Dividends': 'Div.'}, inplace=True)
    current_stock_div.drop(columns=["Description"], inplace=True)

    diff_div = pd.merge(left=div_400, right=current_stock_div[[
                        "Estimation", "Product"]], on="Product")
    diff_div["error"] = diff_div["Estimation"] - diff_div["Paid dividends"]
    st.subheader('diff_div["Estimation"] - diff_div["Paid dividends"]')

    st.dataframe(diff_div, hide_index=True,)

st.sidebar.subheader('Graphs')

if st.sidebar.checkbox("Saving & debt evolution"):
    # start = timeit.default_timer()

    genre = st.radio(
        "Select a graph:",
        ('Saving overview', 'Saving per account', 'Average saving per month'))

    if genre == 'Average saving per month':
        st.subheader('Average saving per month')
        x_months = st.multiselect("Choose the rolling period in months:", [
                                  6, 12, 18, 24, 30, 36, 42, 48])
        if len(x_months) == 0:
            x_months = [12]
        else:
            x_months = x_months

        x_limits = st.multiselect("Exclude months with a saving below:", [
                                  0, -10000, -20000, -30000, -40000, -50000, -200000])
        if len(x_limits) == 0:
            x_limits = -10000
        else:
            x_limits = x_limits[0]
        credit_10 = credit()
        credit_10 = credit_10[credit_10["date"] <= datetime.today()]
        credit_10.rename(
            columns={"date": "Date", "principal": "Total"}, inplace=True)

        # limit=-10000
        all_r = all.copy()
        all_r = all_r[all_r["Description"].str.contains("Achat|Vente")][[
            "Date", "Total"]]
        all_r = all_r.resample('MS', on='Date').sum()["Total"]*(-1)
        all_r = all_r.reset_index()
        tr_sav_r = tr_sav.copy()
        tr_sav_r = tr_sav_r.groupby(["Date"]).sum().reset_index("Date")
        tr_sav_r["Date"] = pd.to_datetime(tr_sav_r["Date"])
        cred = credit_10[["Date", "Total"]]
        coffre = pd.concat([tr_sav_r, all_r, cred]).groupby(
            "Date").sum().reset_index()

        coffre.loc[0, "Total"] = np.nan
        coffre.loc[coffre["Total"] < x_limits, "Total"] = np.nan
        for i in x_months:
            coffre["average_on_{}_months".format(i)] = coffre["Total"].rolling(
                i, min_periods=4).mean()

        # fig = px.line(x=coffre.Date.values, y=coffre.moyenne_glissante.values, color=px.Constant("mean on {} months".format(x_months)))
        fig = px.line(coffre, x=coffre.Date.values, y=[
                      x for x in coffre.columns if "avera" in x])

        fig.add_bar(x=coffre.Date, y=coffre.Total,
                    name="saving per month", marker_color="grey")
        st.plotly_chart(fig, use_container_width=True)

    if genre == 'Saving per account':
        st.subheader('Saving per account')
        tr_sav_group = tr_sav.groupby(["Product", "Date"]).sum(numeric_only=True).groupby(
            level=0).cumsum().reset_index()
        reshape_621 = tr_sav_group.sort_values(
            by="Date", ascending=False).drop_duplicates(subset="Product", keep="first")
        reshape_621 = reshape_621[reshape_621["Total"] != 0]
        # st.dataframe(reshape_621)
        cur_month = str(datetime.today().year) + "-" + \
            str(datetime.today().month) + "-01"
        reshape_621 = reshape_621[reshape_621["Date"] != cur_month]
        reshape_621["Date"] = cur_month
        reshape_621.reset_index(inplace=True, drop=True)
        tr_sav_group = pd.concat([tr_sav_group, reshape_621])
        # st.dataframe(tr_sav_group)

        fig = px.line(tr_sav_group, x="Date", y="Total", color='Product')
        st.plotly_chart(fig, use_container_width=True)

    if genre == 'Saving overview':
        st.subheader('Saving overview')
        data_bal["date"] = data_bal["Date"]
        data_cred = credit_1[["date", "total_debt", 'property_value']]
        data_cred.date = pd.to_datetime(data_cred.date)
        data_2 = data_bal.merge(data_cred, how="left")
        data_2["total_debt"].fillna(method="pad", inplace=True)
        data_2["total_debt"].fillna(0, inplace=True)
        data_2["property_value"].fillna(method="pad", inplace=True)
        data_2["property_value"].fillna(0, inplace=True)

        data_2["debt + saving"] = -data_2["total_debt"]+data_2["Valeur"]
        data_2["debt + saving + property_value"] = - \
            data_2["total_debt"]+data_2["Valeur"] + data_2["property_value"]
        st.write(data_2)
        fig = make_subplots(specs=[[{"secondary_y": False}]])
        # st.dataframe(data_bal)
        # st.dataframe(data_2)
        # Add traces
        fig.add_trace(
            go.Scatter(x=data_bal.Date.values,
                       y=data_bal.Valeur.values, name="saving"),
            secondary_y=False,
        )
        fig.add_trace(
            go.Scatter(x=data_cred.date.values, y=-
                       data_cred.total_debt.values, name="debt"),
            secondary_y=False,
        )
        fig.add_trace(
            go.Scatter(x=data_2.date.values,
                       y=data_2["debt + saving"].values, name="debt + saving"),
            secondary_y=False,
        )
        fig.add_trace(
            go.Scatter(x=data_2.date.values,
                       y=data_2["property_value"].values, name="property_value"),
            secondary_y=False,
        )
        fig.add_trace(
            go.Scatter(x=data_2.date.values,
                       y=data_2["debt + saving + property_value"].values, name="debt + saving + property_value"),
            secondary_y=False,
        )
        fig.add_trace(
            go.Scatter(
                x=r.Date.values, y=r["balance"].values, name="balance (int + div + stocks)"),
            secondary_y=False,
        )

        fig.update_layout(
            # title_text="Portfolio evolution",
            autosize=False,
            width=1200,
            height=600
        )

        fig.update_xaxes(title_text="Time")

        fig.update_yaxes(title_text="<b>Amount</b> €", secondary_y=False)
        st.plotly_chart(fig, use_container_width=True)
        # stop = timeit.default_timer()
        # st.write('Time: ', stop - start)
if st.sidebar.checkbox("Portfolio evolution"):
    st.subheader('Portfolio evolution')

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
        # title_text="Portfolio evolution",
        # autosize=False,
        # width=1600,
        # height=800
    )

    fig.update_xaxes(title_text="Time")

    fig.update_yaxes(title_text="<b>Portfolio</b> €", secondary_y=False)
    fig.update_yaxes(title_text="<b>Balance</b> €", secondary_y=True)
    st.plotly_chart(fig, use_container_width=True)
    stop = timeit.default_timer()
    st.write('Time: ', stop - start)

if st.sidebar.checkbox('Balance per stock'):
    st.subheader('Balance per stock')
    fig = px.bar(all.groupby(by="Product", as_index=False).sum(numeric_only=True).sort_values(by="Total", ascending=False), x=all.groupby(by="Product", as_index=False).sum(numeric_only=True).sort_values(
        by="Total", ascending=False).Product.values, y=all.groupby(by="Product", as_index=False).sum(numeric_only=True).sort_values(by="Total", ascending=False).Total.values)
    fig.update_layout(
        autosize=False,
        width=1100,
        height=800

    )
    st.plotly_chart(fig)


def display_1(height_gr):
    divi = all[all["Description"].str.contains("Divi")].groupby(
        by="Product", as_index=False).sum(numeric_only=True).sort_values(by="Total", ascending=False)
    st.subheader('Cumulated dividend per stock')
    fig = px.bar(divi, x=divi.Product.values, y=divi.Total.values)
    # Add figure title
    fig.update_layout(
        autosize=False,
        width=1200,
        height=height_gr

    )
    return st.plotly_chart(fig, use_container_width=True)


if st.sidebar.checkbox('Cumulated dividend per stock'):

    display_1(800)

if st.sidebar.checkbox('Stock portfolio'):
    st.subheader('Stock portfolio')
    current_stock_div = my_stocks.merge(data_divi, on="Product")
    current_stock_div["% of portfolio"] = round(
        current_stock_div["Total"]/current_stock_div["Total"].values.sum()*100, 1)
    current_stock_div["Total"] = round(current_stock_div["Total"], 1)

    fig = px.pie(current_stock_div, values='% of portfolio',
                 names='Product', hover_data=['Total'])
    fig.update_traces(hole=.4)
    fig.update_layout(annotations=[dict(text=("<b>{} k€</b>").format((int(round(
        current_stock_div.Total.sum()/1000)))), x=0.5, y=0.5, font_size=60, showarrow=False)])

    fig.update_layout(
        # title_text="Portfolio",
        autosize=False,
        width=1200,
        height=800
    )
    st.plotly_chart(fig, use_container_width=True)
    st.write(current_stock_div.Total.sum())

if st.sidebar.checkbox('Savings portfolio', False):
    # st.subheader('Savings portfolio')
    current_stock_div = my_stocks.merge(data_divi, on="Product")
    current_stock_div = pd.concat([pd.DataFrame({"Product": ["Stocks"], "Total": [
                                  current_stock_div.Total.sum()]}), tr_sav.groupby("Product").sum(numeric_only=True).reset_index()])
    # st.write(current_stock_div)
    pa = 325000-credit_1.iloc[len(credit_1.index)-1]["total_debt"]
    current_stock_div = pd.concat([current_stock_div, pd.DataFrame({"Product": [
                                  "Property assets"], "Total": [325000-credit_1.iloc[len(credit_1.index)-1]["total_debt"]]})])
    current_stock_div.reset_index(inplace=True)
    current_stock_div["% of portfolio"] = round(
        current_stock_div["Total"]/current_stock_div["Total"].values.sum()*100, 1)
    current_stock_div["Total"] = round(current_stock_div["Total"], 1)
    current_stock_div.reset_index(inplace=False)
    current_stock_div.drop(
        current_stock_div[current_stock_div["Total"] < 11].index, inplace=True)
    # current_stock_div=pie_saving(my_stocks,data_divi,tr_sav,0,800,800)[1]
    # st.write(current_stock_div)

    # # st.markdown("""
    # # #### <span style="color:white">Total saving: {temp} €</span>
    # # """.format(temp=current_stock_div.Total.sum().round(2)), unsafe_allow_html=True)

    # # st.write(current_stock_div)
    # current_stock_div["amount_k"]=current_stock_div["Total"].apply(lambda x: str((round(x/1000))) +" k€")
    # current_stock_div["Product"]=current_stock_div["Product"]+" - "+ current_stock_div["amount_k"]
    # fig = px.pie(current_stock_div, values='% of portfolio', names='Product',hover_data=['Total'])
    # # Add figure title
    # fig.update_layout(
    #     # autosize=False,
    #     width=1200,
    #     height=800,
    #     annotations=[dict(text=("<b>€{}k</b>").format((int(round(current_stock_div.Total.sum()/1000)))), x=0.5, y=0.5, font_size=60, showarrow=False)],
    # )
    # colours = ['#440154', '#3e4989', '#26828e', '#35b779', '#fde725','#025464']
    # fig.update_traces(textfont_size=120,hole=.4)
    # fig.update_traces(textposition='inside', textinfo='percent+label',textfont_size=25,
    #               marker=dict(line=dict(color='#000000', width=2),
    #                           colors= colours))
    # fig.update(layout_showlegend=False)
    # # st.plotly_chart(fig, use_container_width = True)
    # selected_points = plotly_events(fig)

    # try:
    #     # st.write(selected_points)
    #     click_pie=(current_stock_div.iloc[selected_points[0]["pointNumber"]]["Product"].split("-")[0])

    #     transac_opt=tr_sav1[tr_sav1["Product"].str.contains(click_pie[:-1])].sort_values(by="Date",ascending=False)

    #     if click_pie[:-1]=="Stocks":
    #         transac_opt=all[all["Description"]!="Stock"].copy().sort_values(by="Date",ascending=False)
    #         transac_opt["Date"]=transac_opt["Date"].apply(lambda x: x.strftime("20%y-%m-%d"))
    #         transac_opt["Product"]=transac_opt["Product"].apply(lambda x: x[:30])
    #         transac_opt = transac_opt.fillna(0).style.format(subset=['Quantity','Total','Taxes',"Amount"],formatter="{:.2f}",)
    #     # Inject CSS with Markdown
    #     st.markdown(hide_dataframe_row_index, unsafe_allow_html=True)
    #     st.table(transac_opt)
    # except:
    #     st.write("select a point")

    st.markdown("**Assets overview**")
    sav_d_3 = curve_sav_debt(data_bal, credit_1, 10000)[1]
    tempo_6538 = sav_d_3.loc[(sav_d_3.index)[-1:]]
    p_a = 325000-tempo_6538.total_debt.values[0]
    on = st.toggle("with property assets")
    if on == 0:
        p_a = 0
    # st.plotly_chart(pie_saving(my_stocks,data_divi,tr_sav,p_a)[0],use_container_width=True)
    fig = pie_saving(my_stocks, data_divi, tr_sav, p_a, 800, 800)[0]

    current_stock_div = pie_saving(
        my_stocks, data_divi, tr_sav, p_a, 800, 800)[1]

    # placeholder=st.empty()
    # placeholder.plotly_chart(fig)
    # placeholder.empty()
    # selected_points = plotly_events(fig)
    # fig
    selected_points = plotly_events(fig, override_height=800)
    event = st.plotly_chart(
        fig, use_container_width=True, on_select='rerun')
    st.write(event)
    st.write(current_stock_div)
# st.write(current_stock_div)
    try:
        # st.write(selected_points)
        # st.write(current_stock_div)
        click_pie = (
            current_stock_div.iloc[selected_points[0]["pointNumber"]]["Product"].split("-")[0])
        transac_opt = tr_sav1[tr_sav1["Product"].str.contains(
            click_pie[:-1])].sort_values(by="Date", ascending=False)
        # st.write(click_pie)

        if "Stocks" in click_pie:
            # st.write(all)
            transac_opt = all[all["Description"] != "Stock"].copy(
            ).sort_values(by="Date", ascending=False)
            transac_opt["Date"] = transac_opt["Date"].apply(
                lambda x: x.strftime("20%y-%m-%d"))
            transac_opt["Product"] = transac_opt["Product"].apply(
                lambda x: x[:30])
            transac_opt = transac_opt.fillna(0).style.format(
                subset=['Quantity', 'Total', 'Taxes', "Amount"], formatter="{:.2f}",)
        if "Property asse" in click_pie:
            transac_opt = credit_1.sort_values(by="date", ascending=False)
            transac_opt["property_value"] = 325000
            transac_opt["property_asset"] = transac_opt["property_value"] - \
                transac_opt["total_debt"]

        # Inject CSS with Markdown
        st.markdown(hide_dataframe_row_index, unsafe_allow_html=True)
        st.table(transac_opt)
        # st.dataframe(transac_opt)
    except:
        st.write("select a point")

    # st.write(credit_1)

    # f

if st.sidebar.checkbox('Investment income'):
    st.subheader('Investment income per period')
    col_inv_1, col_inv_2, col_inv_3 = st.columns((1, 1, 1))
    with col_inv_1:
        genre = st.radio(
            "Select a period:",
            ('Year', 'Quarter', 'Month', 'Week'))
    with col_inv_2:
        scale = st.radio("Select the y scale:",
                         ("logarithmic y axis", "linear y axis"),
                         index=1,
                         )
        if scale == "logarithmic y axis":
            scale = True
        else:
            scale = False
    with col_inv_3:
        period = st.radio("Select the period to display:", (
            "2014-present",
            "2016-present",
            "2018-present",
            "2020-present",
            "2022-present"
        ))
    period = period[:4]
    # st.write(int(period))
    interest = tr_sav1[tr_sav1["Description"].isin(["Interest"])]
    xa = all2[all2["Description"].isin(["Dividend"])]
    xa = pd.concat([xa, interest])
    xa["Date"] = pd.to_datetime((xa.Date))
    xa = xa[(xa["Date"].apply(lambda x: int(str(x)[:4]))) >= (int(period))]
    # st.dataframe(xa)

    if genre == 'Year':
        xa_y = pd.DataFrame(xa.resample(
            'A', on='Date', label='right').sum()["Total"])
        xa_y["year"] = xa_y.index
        xa_y["year"] = xa_y["year"].apply(lambda x: x.strftime("20%y"))
        fig = px.bar(xa_y, x=xa_y.year, y="Total")
        xa_y["group"] = "investment revenue"
        fig = px.bar(xa_y, x=xa_y.year, y="Total", color="group", color_discrete_map={
                     'investment revenue': '#6DD6DA'}, log_y=scale)
        fig.update_xaxes(type='category')
        fig.update_layout(title_text="Investement income per {}".format(genre),
                          showlegend=False)
        fig.update_layout({"uirevision": "foo"}, overwrite=True)
        event = st.plotly_chart(
            fig, use_container_width=True, on_select='rerun', selection_mode=('points'))

        try:
            data_to_show = xa.copy()
            data_to_show["year"] = data_to_show["Date"].apply(
                lambda x: x.to_period("y").strftime("20%y"))
            data_to_show = data_to_show[data_to_show["year"] == (
                # selected_points[0]["x"][:7]
                event["selection"]['points'][0]['x']
            )].drop(
                columns=["Price", "Currency", "Quantity", "Taxes", "Amount", "year", "Tickers"], axis=1).groupby("Product").sum(numeric_only=True)
            data_to_show = data_to_show.merge(xa[["Product", "Description"]].drop_duplicates(
                keep="first"), on="Product", how="left")
            st.markdown(hide_dataframe_row_index, unsafe_allow_html=True)
            st.table(data_to_show.sort_values(by="Total", ascending=False)[
                ["Product", "Description", "Total"]].style.format(subset=['Total'], formatter="{:.2f}"))
        except:
            st.write("Click on the plot to display the details")

    if genre == "Quarter":
        xa_q = pd.DataFrame((xa.resample('Q', on='Date', label='right').sum()))
        xa_q["rolling on 4 quarters"] = xa_q.Total.rolling(
            4, min_periods=1).mean()
        xa_q["quarter"] = xa_q.index
        xa_q["quarter"] = pd.to_datetime(xa_q.quarter).apply(
            lambda x: x.to_period("Q").strftime("20%y-Q%q"))
        xa_q["group"] = "investment revenue"
        fig = px.bar(xa_q, x=xa_q.quarter, y="Total", color="group", color_discrete_map={
                     'investment revenue': '#6DD6DA'}, log_y=scale)
        fig.add_trace(
            go.Scatter(
                x=xa_q.quarter,
                y=xa_q["rolling on 4 quarters"]
            ))
        fig.update_layout(title_text="Investement income per {}".format(genre),
                          showlegend=False)
        fig.update_layout({"uirevision": "foo"}, overwrite=True)

        # selected_points = plotly_events(fig, override_height=600)
        event = st.plotly_chart(
            fig, use_container_width=True, on_select='rerun', selection_mode=('points'))

        try:
            xa_per_quarter = xa.copy()
            xa_per_quarter["year_quarter"] = xa_per_quarter["Date"].apply(
                lambda x: x.to_period("Q").strftime("20%y-Q%q"))
            st.markdown(hide_dataframe_row_index, unsafe_allow_html=True)
            xa_per_quarter["Date"] = pd.to_datetime(
                xa_per_quarter["Date"]).apply(lambda x: x.strftime("20%y-%m-%d"))
            st.table(xa_per_quarter[xa_per_quarter["year_quarter"] == (event["selection"]['points'][0]['x'])].drop(columns=["Price", "Currency", "Quantity", "Taxes",
                     "Amount", "year_quarter", "Tickers"], axis=1).sort_values(by="Total", ascending=False).style.format(subset=['Total'], formatter="{:.2f}"))
        except:
            st.write("Click on the plot to display the details")

    if genre == "Month":
        xa_m = xa.resample('MS', on='Date').sum()["Total"]
        xa_m = pd.DataFrame(xa_m)
        xa_m["rolling on 12 months"] = xa_m.Total.rolling(
            12, min_periods=1).mean()
        xa_m["group"] = "investment revenue"
        fig = px.bar(xa_m, x=xa_m.index, y="Total", color="group", color_discrete_map={
                     'investment revenue': '#6DD6DA'}, height=600, log_y=scale)
        fig = fig.add_trace(
            go.Scatter(
                x=xa_m.index,
                y=xa_m["rolling on 12 months"],
                name="average on 12 months"
            ))
        fig.update_layout(title_text="Investement income per {}".format(genre),
                          showlegend=False)
        fig.update_layout({"uirevision": "foo"}, overwrite=True)

        event = st.plotly_chart(
            fig, use_container_width=True, on_select='rerun', selection_mode=('points'))
        try:
            point_month = event["selection"]['points'][0]['x'][:7]
            xa_per_month = xa.copy()
            xa_per_month["year_month"] = xa_per_month["Date"].apply(
                lambda x: x.strftime("20%y-%m"))
            st.markdown(hide_dataframe_row_index, unsafe_allow_html=True)
            data_month = xa_per_month[xa_per_month["year_month"] == point_month].drop(
                columns=["Price", "Currency", "Quantity", "Taxes", "Amount", "year_month", "Tickers"], axis=1).sort_values(by="Total", ascending=False)
            data_month["Date"] = pd.to_datetime(data_month["Date"]).apply(
                lambda x: x.strftime("20%y-%m-%d"))
            st.table(data_month.style.format(
                subset=['Total'], formatter="{:.2f}"))
        except:
            st.write("Click on the plot to display the details")

    if genre == "Week":
        xa_w = xa.resample('W-MON', on='Date', label='left').sum()
        xa_w["CW"] = xa_w.index
        xa_w["CW"] = xa_w["CW"].apply(lambda x: str(
            x.isocalendar()[0]) + " -CW" + str(x.isocalendar()[1]))
        xa_w["rolling on 52 weeks"] = xa_w.Total.rolling(
            53, min_periods=1).mean()
        xa_w["group"] = "investment revenue"

        fig = px.bar(xa_w, x=xa_w.CW, y="Total", color="group", color_discrete_map={
                     'investment revenue': '#6DD6DA'}, height=600, log_y=scale)
        fig.add_trace(
            go.Scatter(
                x=xa_w.CW,
                y=xa_w["rolling on 52 weeks"]
            ))
        # st.write(xa_w)
        fig.update_layout(
            autosize=True,
            # width=500,
            # height=900,
            margin=dict(
                l=50,
                r=50,
                b=150,
                t=100,
                pad=4
            ),
        )
        fig.update_layout(title_text="Investement income per {}".format(genre),
                          showlegend=False)
        fig.update_layout({"uirevision": "foo"}, overwrite=True)

        event = st.plotly_chart(
            fig, use_container_width=True, on_select='rerun', selection_mode=('points'))
        try:
            point_week = event["selection"]['points'][0]['x']
            xa_w = xa.copy()
            xa_w["year_week"] = xa_w["Date"].apply(lambda x: str(
                x.isocalendar()[0]) + " -CW" + str(x.isocalendar()[1]))
            st.markdown(hide_dataframe_row_index, unsafe_allow_html=True)
            data_week = xa_w[xa_w["year_week"] == point_week].drop(
                columns=["Price", "Currency", "Quantity", "Taxes", "Amount", "year_week", "Tickers"], axis=1).sort_values(by="Total", ascending=False)
            data_week["Date"] = pd.to_datetime(data_week["Date"]).apply(
                lambda x: x.strftime("20%y-%m-%d"))
            st.table(data_week.style.format(
                subset=['Total'], formatter="{:.2f}"))
        except:
            st.write("Click on the plot to display the details")

st.sidebar.subheader('Data input')

if st.sidebar.checkbox("Dividend per share"):
    # div_int=pd.read_csv("data/dividend_list_int")
    # st.session_state.exp_data_frame = st.experimental_data_editor(div_int)
    div_int = pd.read_csv("data/dividend_list")

    df = st.data_editor(div_int, use_container_width=True,
                        height=1200, num_rows="dynamic")
    st.write("  ")
    if st.button(label="Submit modification", use_container_width=True):
        df.to_csv("data/dividend_list", index=False)

if st.sidebar.checkbox("Savings change"):
    # div_int=pd.read_csv("data/dividend_list_int")
    # st.session_state.exp_data_frame = st.experimental_data_editor(div_int)
    div_int_g = pd.read_csv("data/saving")

    dg = st.data_editor(div_int_g, use_container_width=True,
                        height=1200, num_rows="dynamic")
    st.write("  ")
    if st.button(label="Submit modification", use_container_width=True):
        dg.to_csv("data/saving", index=False)

if st.sidebar.checkbox("Interest rates"):
    # div_int=pd.read_csv("data/dividend_list_int")
    # st.session_state.exp_data_frame = st.experimental_data_editor(div_int)
    div_int_g = pd.read_csv("data/interest")

    dg = st.data_editor(
        div_int_g, use_container_width=True, num_rows="dynamic")
    st.write("  ")
    if st.button(label="Submit modification", use_container_width=True):
        dg.to_csv("data/interest", index=False)

    # edited_df = st.experimental_data_editor(div_int)
    # if 'exp_data_frame' not in st.session_state:
    #     st.session_state.exp_data_frame = st.experimental_data_editor(div_int, on_change=)
    #     output_df = st.session_state.exp_data_frame
    #     output_df.to_csv("data/dividend_list_int", index = False)

    # else:
    #     output_df = st.experimental_data_editor(
    #         st.session_state.exp_data_frame
    #         )
    #     output_df.to_csv("data/dividend_list_int", index = False)


def save_uploadedfile(uploadedfile):
    with open(os.path.join(r"C:\Users\loicg\Downloads", "test.csv"), "wb") as f:
        f.write(uploadedfile.getbuffer())
    return st.success("Saved File:{} to tempDir".format("test"))


if st.sidebar.checkbox("Account statement"):
    # div_int_g=pd.read_csv("data/interest")
    # os.chdir(r"C:\Users\loicg\OneDrive\Documents\IT\banking\data")
    # st.write(os.listdir())
    uploaded_files = st.file_uploader("Choose a CSV file", type=[
                                      "csv"], accept_multiple_files=True)
    for uploaded_file in uploaded_files:
        name_file = "dummy"
        if "Beschreibung" in str(uploaded_file.getvalue()):
            name_file = "DEGIRO " + \
                str(date.today().strftime("%Y%m%d")) + str(".csv")
        if "Courtage" in str(uploaded_file.getvalue()):
            name_file = "FORTUNEO " + \
                str(date.today().strftime("%Y%m%d")) + str(".csv")
        if (("DEGIRO" in name_file) or ("FORTUNEO" in name_file)):
            with open(os.path.join(r"C:\Users\loicg\OneDrive\Documents\IT\banking\data", name_file), "wb") as f:
                f.write(uploaded_file.getbuffer())
            st.write("Saved File:" + " " + (str(name_file)))

        else:
            st.write("File must be generated from DEGIRO or FORTUNEO")


############################## TEST DASHBOARD#########################################


st.sidebar.subheader('Simulator')
if st.sidebar.checkbox("Future buying"):
    ##### Préparation###
    list_qt = pd.read_csv("data/list_qt")
    list_cur = stock_final2[stock_final2["Currency"].str.contains(
        "=", na=False)]
    list_cur = list_cur.sort_values(by="Date", ascending=True).drop_duplicates(
        subset=["Currency"], keep="last")[["Currency", "Close"]]
    list_cur["Currency"] = list_cur["Currency"].apply(lambda x: x[:3])
    list_cur = pd.concat([list_cur, pd.DataFrame(
        {"Currency": ["EUR"], "Close": [1]})])
    list_cur.rename(columns={"Close": "Change"}, inplace=True)
    list_cur.loc[list_cur["Currency"] == "GBp",
                 "Change"] = list_cur.loc[list_cur["Currency"] == "GBp", "Change"]/100
    # st.dataframe(list_cur)
    list_st = pd.merge(left=stock_final2, right=list_cur, on="Currency")
    list_st = list_st.sort_values(by="Date", ascending=True).drop_duplicates(
        subset=["Tickers"], keep="last")
    list_st = pd.merge(left=list_st, right=t_list, on="Tickers")
    list_st = pd.merge(left=list_st, right=data_divi, on="Product")
    list_st = pd.merge(left=list_st, right=list_qt, on="Product")
    list_st["Dividends_net"] = list_st["Dividends"] * \
        list_st["Net"]*list_st["Quantity"] * st.session_state["df"]["Change"]
    list_st["Value"] = list_st["Quantity"]*list_st["Change"]*list_st["Close"]
    list_st = list_st[["Product", "Close", "Currency", "Change",
                       "Dividends", "Net", "Quantity", "Value", "Dividends_net"]]

    # edited_list_st=st.experimental_data_editor(list_st, use_container_width=True,height=1200,num_rows="dynamic")
    # list_st["Value"]=list_st["Quantity"] * list_st["Change"] * list_st["Close"]

    def update_value(new_df: pd.DataFrame | None = None):
        if new_df is not None:
            if new_df.equals(st.session_state["df"]):
                return
            st.write('line 1266')
            st.session_state["df"] = new_df

        st.session_state["df"]["Value"] = 0
        st.session_state["df"]["Value"] = (
            st.session_state["df"]["Quantity"] *
            st.session_state["df"]["Change"] * st.session_state["df"]["Close"]
        )
        st.session_state["df"]["Dividends_net"] = (
            st.session_state["df"]["Quantity"]
            * st.session_state["df"]["Change"] *
            st.session_state["df"]["Dividends"] * st.session_state["df"]["Net"]
        )
        # st.experimental_rerun()

    if "df" not in st.session_state:
        st.session_state.df = list_st

    editable_df = st.data_editor(
        list_st, key="data", height=1600, use_container_width=True)
    update_value(editable_df)
    st.write("Stocks table with quantity > 0")
    st.write(editable_df[editable_df["Quantity"] > 0])
    st.write("Total value: {} €".format(
        st.session_state["df"]["Value"].sum().round(2)))
    st.write("Total dividends: {} €".format(
        st.session_state["df"]["Dividends_net"].sum().round(2)))
    if st.button(label="Submit modification", use_container_width=True):
        editable_df[["Product", "Quantity"]].to_csv(
            "data/list_qt", index=False)

if st.sidebar.checkbox("Future saving"):
    st.subheader('Future saving')

    tot_sav = data_bal.Valeur.values[-1]
    sell_value = st.slider(
        'Select the estimated value of your property',
        min_value=0, max_value=450000, value=325000, step=1000)
    amount = st.slider(
        'Select a saving amount', min_value=0, max_value=5000, value=2500, step=100)

    from bank_fct import credit

    tab_cred = credit()
    start_date = datetime(datetime.today().year, datetime.today().month, 15)
    end_date = datetime(2030, 1, 1)
    import math
    time_range_2 = st.slider(
        'Select a range of time',
        min_value=start_date, max_value=end_date, format="YYYY/MM", step=timedelta(days=30.4), value=datetime(2026, 1, 1))
    month_m = round((time_range_2-start_date).days/30.4)
    target_m = datetime(time_range_2.year, time_range_2.month, 1)
    debt_m = tab_cred[tab_cred["date"] == target_m]["total_debt"].values[0]
    result = tot_sav+amount*month_m+sell_value-debt_m
    v1, v2, v3, v4 = st.columns((1, 1, 1, 1))
    w1, w2, w3 = st.columns((1, 1, 1))
    with v1:
        st.metric(label="Saving in {}:".format(datetime.today().strftime(
            "%B %y")), value='{:,}'.format((round(tot_sav))).replace(',', ' ') + " €")
    with v2:
        st.metric(label="Saved amount after {} months:".format(
            month_m), value='{:,}'.format((round(amount*month_m))).replace(',', ' ') + " €")

    # st.write("Total saving after {} months: {} €".format(month_m,round(amount*month_m+tot_sav)))
    with v3:
        st.metric(label="Total saving after {} months:".format(month_m), value='{:,}'.format(
            (round(amount*month_m+tot_sav))).replace(',', ' ') + " €")

    # st.write("Future debt after {} months: {} €".format(month_m,round(debt_m)))
    with v4:
        st.metric(label="Future debt in {} :".format(time_range_2.strftime(
            "%B %y")), value='{:,}'.format((round(debt_m))).replace(',', ' ') + " €")

    # st.write("Down payment possible in {}: {} €".format(time_range_2.strftime("%B %y"),round(result)))
    with w2:
        st.metric(label="Down payment possible in {}:".format(time_range_2.strftime(
            "%B %y")), value='{:,}'.format((round(result))).replace(',', ' ') + " €")

if st.sidebar.checkbox("Incomes and expenses"):
    ##### Préparation###
    gr_1, gr_2, gr_3 = st.columns([1, 1, 1])
    inv_inc = call_div_int(tr_sav, my_stocks, data_divi).iloc[-1, :][1]
    # st.write(call_div_int(tr_sav, my_stocks, data_divi))

    def update_value_2(new_df: pd.DataFrame | None = None):
        if new_df is not None:
            if new_df.equals(st.session_state["df2"]):
                return
            st.session_state["df2"] = new_df
        st.experimental_rerun()

    list_ie = pd.read_csv(r"data/expenses_incomes.csv",
                          encoding='latin1', delimiter=";|,").sort_values(by="category")
    list_ie.loc[list_ie["description"] ==
                "investement income", "amount"] = round(inv_inc/12, 1)
    # list_ie.to_csv("data/expenses_incomes.csv", index=False, encoding="latin1")
    # st.write(list_ie)

    if "df2" not in st.session_state:
        st.session_state.df2 = list_ie
    # update_value_2(list_ie)

    editable_df2 = st.data_editor(
        st.session_state["df2"], key="data", height=1600, use_container_width=True, num_rows="dynamic")
    # update_value_2(editable_df2)
    if st.button(label="Submit modification", use_container_width=True):
        editable_df2[["category", "description", "amount"]].to_csv(
            "data/expenses_incomes.csv", index=False, encoding="latin1")
        update_value_2(list_ie)

    # st.write(st.session_state["df2"].groupby(by="category").sum())
    budget_gr = st.session_state["df2"].groupby(
        by="description").sum().reset_index()
    budget_gr = budget_gr[budget_gr["amount"] < 0]
    budget_gr["amount"] = budget_gr["amount"]*(-1)

    budget_gr2 = st.session_state["df2"].groupby(
        by="category").sum().reset_index()
    budget_gr2 = budget_gr2[budget_gr2["amount"] < 0]
    budget_gr2["amount"] = budget_gr2["amount"]*(-1)
    income_gr = st.session_state["df2"].groupby(
        by="description").sum().reset_index()
    income_gr = income_gr[income_gr["amount"] > 0]

    fig = px.pie(budget_gr, values="amount", names="description")
    fig.update_traces(textposition='inside', textinfo='percent+label', textfont_size=25,
                      marker=dict(line=dict(color='#000000', width=2),
                                  #   colors= colours
                                  )
                      )
    fig.update_traces(hole=.4)
    fig.update(layout_showlegend=False)
    fig.update_layout(
        title_text="Budget",
        width=600,
        height=600,
        annotations=[dict(text=("<b>{} €</b>").format((int(round(budget_gr.amount.sum())))),
                          x=0.5, y=0.5, font_size=45, showarrow=False)],
    )

    fig3 = px.pie(budget_gr2, values="amount", names="category")
    fig3.update_traces(textposition='inside', textinfo='percent+label', textfont_size=25,
                       marker=dict(line=dict(color='#000000', width=2),
                                   #   colors= colours
                                   )
                       )
    fig3.update_traces(hole=.4)
    fig3.update(layout_showlegend=False)
    fig3.update_layout(
        title_text="Budget",
        width=600,
        height=600,
        annotations=[dict(text=("<b>{} €</b>").format((int(round(budget_gr2.amount.sum())))),
                          x=0.5, y=0.5, font_size=45, showarrow=False)],
    )
    with gr_1:
        st.plotly_chart(fig, use_container_width=True)

    fig2 = px.pie(income_gr, values="amount", names="description")
    fig2.update_traces(textposition='inside', textinfo='percent+label', textfont_size=25,
                       marker=dict(line=dict(color='#000000', width=2),
                                   #   colors= colours
                                   )
                       )
    fig2.update_traces(hole=.4)
    fig2.update(layout_showlegend=False)
    fig2.update_layout(
        title_text="Incomes",
        width=600,
        height=600,
        annotations=[dict(text=("<b>{} €</b>").format((int(round(income_gr.amount.sum())))),
                          x=0.5, y=0.5, font_size=45, showarrow=False)],
    )
    with gr_2:
        st.plotly_chart(fig3, use_container_width=True)
    with gr_3:
        st.plotly_chart(fig2, use_container_width=True)

    # fig = px.pie(current_stock_div, values='% of portfolio', names='Product',hover_data=['Total'])
    # fig.update_traces(hole=.4)
    # fig.update_layout(annotations=[dict(text=("<b>{} k€</b>").format((int(round(current_stock_div.Total.sum()/1000)))), x=0.5, y=0.5, font_size=60, showarrow=False)])

    # fig.update_layout(
    #     # title_text="Portfolio",
    #     autosize=False,
    #     width=1200,
    #     height=600
    # )
    # st.plotly_chart(fig,use_container_width=True)

if st.sidebar.checkbox("Cars follow-up"):
    def update_value_2(new_df: pd.DataFrame | None = None):
        if new_df is not None:
            if new_df.equals(st.session_state["df3"]):
                return
            st.session_state["df3"] = new_df
        st.experimental_rerun()

    list_events = pd.read_csv(r"data/car_events.csv",
                              encoding='latin1', sep=',')
    # list_events.loc[list_events["description"] =="investement income", "amount"] = round(inv_inc/12, 1)
    # list_ie.to_csv("data/car_events.csv", index=False, encoding="latin1")
    st.header('Data input')

    # if "df3" not in st.session_state:
    st.session_state.df3 = list_events
    # update_value_2(list_ie)

    editable_df3 = st.data_editor(
        st.session_state["df3"], key="data", use_container_width=True, num_rows="dynamic")
    # update_value_2(editable_df2)
    if st.button(label="Submit modification", use_container_width=True):
        editable_df3.to_csv(
            "data/car_events.csv", index=False, encoding="latin1", sep=',')
        update_value_2(list_events)
    # st.write(st.session_state["df3"].price.sum())
    petrol_price = pd.read_csv(
        r"data/petrol_price", encoding='latin1', sep=',')
    # petrol_price = petrol_price[petrol_price["TVA"]=="TVAC"]
    my_df_3 = st.session_state.df3

    petrol_price = petrol_price.iloc[:, 1:-1]
    petrol_price["Date"] = pd.to_datetime(
        petrol_price["Date"], format="%d/%m/%Y")

    petrol_price = petrol_price.set_index('Date').stack().reset_index(
        name='Price').rename(columns={'level_1': 'Product'})
    petrol_price = petrol_price.sort_values(by="Date", ascending=True)
    # petrol_price = petrol_price[:-5]
    # st.write(petrol_price.describe())
    # st.write(petrol_price.dtypes)
    # st.write(petrol_price)
    diesel = petrol_price.loc[petrol_price['Product'] == 'Diesel']
    today = datetime.today()
    st.write(today.year)
    my_time = pd.date_range(
        start="2014-01-01", end=f"{today.year}-{today.month}-{today.day}", freq="D")
    my_time = pd.DataFrame({'date': my_time.values})

    diesel = pd.merge(left=my_time, right=diesel,
                      left_on='date', right_on='Date', how='left')
    diesel["Price"] = diesel["Price"].fillna(method="ffill")

    my_df_3['date'] = my_df_3['date'].apply(lambda x: date(
        int(x.split('.')[2]), int(x.split('.')[1]), int(x.split('.')[0])))
    my_df_3['date'] = pd.to_datetime(my_df_3['date'])

    my_df_3 = pd.merge(left=diesel, right=my_df_3,
                       left_on='date', right_on='date', how='outer')
    my_df_3 = my_df_3.fillna(np.nan)
    my_df_3['date'] = my_df_3.apply(
        lambda row: row['Date'] if pd.isna(row['date']) else row['date'], axis=1)
    my_df_3 = my_df_3.sort_values(by='date', ascending=True)
    my_df_3['km'] = my_df_3['km'].interpolate(method='linear')
    my_df_3['km_dif'] = my_df_3['km'].diff()
    my_df_3['date_dif'] = my_df_3['date'].diff()
    my_df_3['diesel_cost'] = 4.8*my_df_3['Price']*my_df_3['km_dif']/100
    my_df_3.dropna(subset=['km'], inplace=True)

    my_df_3['diesel_cost_cum'] = my_df_3['diesel_cost'].cumsum()
    my_df_3['car_cost_cum'] = my_df_3['price'].cumsum()
    my_df_3["car_cost_cum"] = my_df_3["car_cost_cum"].fillna(method="ffill")
    my_df_3['all_cost_volvo_V40'] = my_df_3['diesel_cost_cum'] + \
        my_df_3["car_cost_cum"]

    st.write(my_df_3)
    c1, c2, c3 = st.columns(3)
    with c1:
        st.write('Diesel cost: ',
                 f'{round(my_df_3.diesel_cost.sum(),2):,} €'.replace(",", " "))
    with c2:
        st.write('Vehicule cost: ',
                 f'{round(st.session_state.df3.price.sum(),2):,} €'.replace(",", " "))
    with c3:
        st.write('Total cost: ',
                 f'{round(st.session_state.df3.price.sum()+my_df_3.diesel_cost.sum(),2):,} €'.replace(",", " "))

    # fig = px.line(petrol_price, x="Date", y="Price", color='Product')
    # st.plotly_chart(fig)
    fig = go.Figure()

    # Diesel Cost (Primary Y-Axis)
    fig.add_trace(go.Scatter(
        x=my_df_3["km"], y=my_df_3["diesel_cost_cum"],
        mode="lines+markers",
        name="Diesel Cost",
        line=dict(color="blue", width=2),
        yaxis="y1"
    ))

    # Car Cost (Secondary Y-Axis)
    fig.add_trace(go.Scatter(
        x=my_df_3["km"], y=my_df_3["car_cost_cum"],
        mode="lines+markers",
        name="Car Cost",
        line=dict(color="red", width=2, dash="dot"),
        yaxis="y2"
    ))

    # Layout
    fig.update_layout(
        title="Diesel Cost & Car Cost vs Kilometer",
        xaxis=dict(title="Kilometers"),
        yaxis=dict(
            title="Diesel Cost (€)",
            # titlefont=dict(color="blue"),
            tickfont=dict(color="blue"),
        ),
        yaxis2=dict(
            title="Car Cost (€)",
            # titlefont=dict(color="red"),
            tickfont=dict(color="red"),
            overlaying="y",
            side="right"
        ),
        legend=dict(x=0.05, y=0.95),
        template="plotly_white"
    )

    # Show Figure
    st.plotly_chart(fig)
    fig2 = go.Figure()

    fig2.add_trace(go.Scatter(
        x=my_df_3["km"],
        y=my_df_3["all_cost_volvo_V40"],
        mode="lines+markers",
        name="Total Cost (Volvo V40)",
        line=dict(color="darkgreen", width=3),
        marker=dict(size=6)
    ))

    # Layout Customization
    fig2.update_layout(
        title="Total Cost of Volvo V40 Over Distance",
        xaxis=dict(title="Kilometers Driven"),
        yaxis=dict(title="Total Cost (€)"),
        template="plotly_white",
        hovermode="x"
    )
    st.plotly_chart(fig2)

    # Create figure
    fig3 = go.Figure()

    # Add Total Cost Line
    fig3.add_trace(go.Scatter(
        x=my_df_3["km"],
        y=my_df_3["all_cost_volvo_V40"],
        mode="lines+markers",
        name="Total Cost (Volvo V40)",
        line=dict(color="darkgreen", width=3),
        marker=dict(size=6)
    ))

    # Update layout for dual X-axis
    fig3.update_layout(
        title="Total Cost of Volvo V40 Over Distance & Time",
        xaxis=dict(
            title="Kilometers Driven",
            side="bottom"
        ),
        xaxis2=dict(
            title="Time (e.g., Date or Month)",
            overlaying="x",
            side="top"
        ),
        yaxis=dict(title="Total Cost (€)"),
        template="plotly_white",
        hovermode="x"
    )

    fig3.update_layout(
        xaxis2=dict(
            title="Date",
            tickvals=my_df_3["km"],
            ticktext=my_df_3["date"].dt.strftime("%Y-%m"),
            overlaying="x",
            side="top"
        )
    )
    st.plotly_chart(fig3)

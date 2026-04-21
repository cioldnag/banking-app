import streamlit as st
import pandas as pd
import numpy as np
from tools import tools
import pandas as pd
import datetime
from datetime import date
import re
import os
pd.options.display.max_columns=200
import os
import shutil
import pandas as pd
from tempfile import NamedTemporaryFile
import subprocess
import sys
import plotly.graph_objects as go
import plotly.express as px
from tools.tools import apply_id,normalize_date,normalize_decimal,latest_fortuneo,latest_degiro,load_base_history,merge_w_tickers,normalize_degiro,normalize_fortuneo,compute_dividends_degiro,compute_dividends_fortuneo,compute_transactions_fortuneo,extract_quantity,compute_transactions_degiro,apply_id

from tools.tools import process_csv_incremental,log_added_rows,convert_prices_to_eur,compute_portfolio_value_from_prices_positions,append_df_to_csv,transac_to_portfolio,transac_to_df, date_stock,sav_int_prop,build_car_value_series

from tools.tools import my_debt
from tools.tools import transac_to_portfolio
# from tools.stock_update import update_stock_values

st.set_page_config(page_title="Portfolio Dashboard", layout="wide")

st.title("📊 Portfolio Dashboard")
# Load data from session state
# if "portfolio" not in st.session_state:
#     st.warning("No data loaded yet. Go to **Input Data** page.")

# if st.button('Update stock'):
#     subprocess.run([f"{sys.executable}", "tools/stock_update.py"])
# @st.cache_data(show_spinner=False)

def load_portfolio_data(x):
    portfolio = transac_to_portfolio('master_data/transactions_master')
    df_all = transac_to_df('master_data/transactions_master')
    prices_daily, stock_cur, full_index = date_stock()

    prices_daily['GBpEUR=X'] = prices_daily['GBpEUR=X'] / 100
    prices_daily = convert_prices_to_eur(prices_daily, stock_cur)

    portfolio = portfolio.reindex(full_index).bfill()
    my_stock_evo = pd.DataFrame(
        compute_portfolio_value_from_prices_positions(prices_daily, portfolio)[0]
    ).rename(columns={0: 'stock'})

    my_saving = sav_int_prop('master_data/saving')
    my_debt_df = my_debt()

    patrimoine = pd.concat([
        my_saving['Saving'],
        my_saving['Property'],
        my_stock_evo,
        (-1) * my_debt_df
    ], axis=1).fillna(0)
    
    my_inc_stock_tot={}
    for i in df_all.keys():
        # print(i)
        my_inc_stock_tot[i]=pd.DataFrame(df_all[i].sum(axis=1)).rename(columns={0:i})

    start_bal_st =my_inc_stock_tot['Achat'].index.values[0]
    my_balance = pd.concat([
        my_inc_stock_tot['Vente'],
        my_inc_stock_tot['Achat'],
        my_inc_stock_tot['Kapitalrückzahlung'],
        my_inc_stock_tot['Dividende'],
        my_inc_stock_tot['Barausgleich'],
        my_stock_evo
        ], axis=1).fillna(0)
    my_balance=pd.DataFrame(my_balance.sum(axis=1))
    my_balance=my_balance[my_balance.index>start_bal_st]

    all_balance = pd.concat([my_balance,my_saving['Interest']],axis=1)

    return patrimoine, portfolio,df_all, all_balance,my_stock_evo

if st.button("Update stocks"):
    # update_stock_values()
    exec(open("tools/stock_update.py").read())
    # st.rerun()

    # exec(open("tools/stock_update.py").read())
# if st.checkbox('load_data'):
patrimoine, portfolio, df_all,all_balance,my_stock_evo = load_portfolio_data(datetime.datetime.today())




car_df_volvo = build_car_value_series(
    date_index=patrimoine.index,
    car_name="Volvo_V40",
    buy_value=17500,
    buy_date="2019-01-30",
    depreciation_rate=0.12,   # 18% per year
)
car_df_volkswagen = build_car_value_series(
    date_index=patrimoine.index,
    car_name="Volkswagen_Polo",
    buy_value=7500,
    buy_date="2020-01-15",
    depreciation_rate=0.10,   # 18% per year
)

patrimoine = patrimoine.join(car_df_volvo)
patrimoine = patrimoine.join(car_df_volkswagen)





st.divider()
st.subheader("📊 Asset distribution - Pie chart")

# Choose dataset
df= patrimoine.copy()
df["property"] = patrimoine["Mettlach-Wehingen"] + patrimoine["total_debt"]
exclude_cols = {"date", "Mettlach-Wehingen", "total_debt"}
value_cols = [c for c in df.columns if c not in exclude_cols]

all_assets = [c for c in patrimoine.columns if c not in {"date", "Mettlach-Wehingen", "total_debt"}]
all_assets.append("property")

# Use a stable color palette
palette = px.colors.qualitative.Safe + px.colors.qualitative.Set2 + px.colors.qualitative.Pastel

color_map = {asset: palette[i % len(palette)] for i, asset in enumerate(all_assets)}

left_1,left_2,right = st.columns((1,1,5))
with left_1:
    if st.toggle("Without property"):
        value_cols.remove('property')
with left_2:      
    if st.toggle("Without car"):
        value_cols.remove('Volkswagen_Polo')
        value_cols.remove('Volvo_V40')
    
    
df=df[value_cols].copy()
if isinstance(df.index, pd.DatetimeIndex):
    df = df.reset_index().rename(columns={"index": "date"})
df["date"] = pd.to_datetime(df["date"])

value_cols = [c for c in df.columns if c != "date"]
dates = sorted(df["date"].unique())

selected_date = st.select_slider(
    "Select portfolio date",
    options=dates,
    format_func=lambda x: x.strftime("%Y-%m-%d"),
    value=dates[-1]
)

row = df[df["date"] == selected_date][value_cols].iloc[0]
labels = value_cols
values = row.values
total_value = values.sum()

labels = [l for l, v in zip(labels, values) if v != 0]
values = [v for v in values if v != 0]

slice_colors = [color_map[label] for label in labels]

fig = go.Figure(data=[go.Pie(
    labels=labels,
    values=values,
    hole=0.55,
    sort=False,
    textinfo="label+percent",
    marker=dict(colors=slice_colors)  # 🔥 THIS LOCKS COLORS
)])

fig.update_layout(
    title=f"Portfolio Allocation — {selected_date.strftime('%Y-%m-%d')}",
    annotations=[dict(
        text=f"<b>{total_value:,.0f} €</b>",
        x=0.5, y=0.5,
        font_size=26,
        showarrow=False
    )],
    height=500,
    margin=dict(t=60, b=20, l=20, r=20)
)
fig.update_traces(sort=False)
fig.update_layout(legend_traceorder="normal")
st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
st.divider()

all_balance.rename(columns={0:'stock_balance'},inplace=True)
# st.write(all_balance)

# st.write(my_stock_evo)
stock_follow_up= pd.concat([all_balance.stock_balance,my_stock_evo.stock],axis=1)
pat=patrimoine.sum(axis=1).to_frame(name='patrimoine')
pat_bal = all_balance.sum(axis=1).to_frame(name='patrimoine_balance')

# st.write(stock_follow_up)
import plotly.graph_objects as go

# Make sure date column is datetime
# stock_follow_up['date'] = pd.to_datetime(stock_follow_up['date'])

fig = go.Figure()

# Curve 1: Stock Balance
fig.add_trace(go.Scatter(
    x=stock_follow_up.index,
    y=stock_follow_up['stock_balance'],
    mode='lines',
    name='Stock Balance',
    line=dict(width=3)
))

# Curve 2: Stock
fig.add_trace(go.Scatter(
    x=stock_follow_up.index,
    y=stock_follow_up['stock'],
    mode='lines',
    name='Stock',
    line=dict(width=3,
            #   dash='dash'
              )
))

fig.add_trace(go.Scatter(
    x=pat.index,
    y=pat['patrimoine'],
    mode='lines',
    name='patrimoine',
    line=dict(width=3,
            #   dash='dash'
              )
))
fig.add_trace(go.Line(
    x=pat_bal.index,
    y=pat_bal['patrimoine_balance'],
    mode='lines',
    name='patrimoine_balance',
    line=dict(width=3,
            #   dash='dash'
              )
))



# Layout styling
fig.update_layout(
    height=700,

    title=dict(
        text='Stock vs Stock Balance Over Time',
        x=0.5,  # center title
        xanchor='center',
    ),
    xaxis=dict(
        title='Date',
        showgrid=True
    ),
    yaxis=dict(
        title='Quantity',
        showgrid=True
    ),
    legend=dict(
        title='Legend',
        orientation='h',
        yanchor='bottom',
        y=1.02,
        xanchor='right',
        x=1
    ),
    template='plotly_white',
    margin=dict(l=60, r=40, t=80, b=80)
)

# Footnote (annotation at bottom)
fig.add_annotation(
    text="Source: stock_follow_up dataframe",
    xref="paper", yref="paper",
    x=0, y=-0.18,
    showarrow=False,
    font=dict(size=12, color="gray")
)

st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
st.divider()

# st.write('patrimoine',patrimoine.sum(axis=1).to_frame(name='patrimoine'),'all_balance',all_balance.sum(axis=1).to_frame(name='patrimoine_balance'))

# st.write(patrimoine)

df=patrimoine.copy()
df.index = pd.to_datetime(df.index)
# df['total_debt'] = -df['total_debt']
stock_cols = ["stock"]
property_cols = ["Mettlach-Wehingen", 'total_debt']
car_cols = ["Volvo_V40", 'Volkswagen_Polo']

debt_cols = ["total_debt"]

excluded = stock_cols + property_cols + debt_cols+car_cols
savings_cols = [c for c in df.columns if c not in excluded]
wealth = pd.DataFrame(index=df.index)

wealth["Savings"] = df[savings_cols].sum(axis=1)
wealth["Stock"] = df[stock_cols].sum(axis=1)
wealth["Property"] = df[property_cols].sum(axis=1)
wealth["Car"] = df[car_cols].sum(axis=1)

wealth["Debt"] = df[debt_cols].sum(axis=1)

# Net wealth
wealth["Net_Worth"] = (
    wealth["Savings"]
    + wealth["Stock"]
    + wealth["Property"]
    # - wealth["Debt"]
)
yearly = wealth.resample("Y").last()
yearly.index = yearly.index.year  # cleaner index
yoy = yearly.diff()
yoy.columns = [c + "_YoY" for c in yoy.columns]

summary = pd.concat([yearly, yoy], axis=1)
yoy_pct = yearly.pct_change() * 100
yoy_pct.columns = [c + "_YoY_%" for c in yoy_pct.columns]

summary = pd.concat([yearly, yoy, yoy_pct], axis=1)
st.subheader("📆 Yearly Wealth Summary")
st.dataframe(summary.style.format("{:,.0f}"))


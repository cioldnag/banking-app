import streamlit as st
import pandas as pd
import numpy as np
import datetime
from tools.tools import apply_id,normalize_date,normalize_decimal,latest_fortuneo,latest_degiro,load_base_history,merge_w_tickers,normalize_degiro,normalize_fortuneo,compute_dividends_degiro,compute_dividends_fortuneo,compute_transactions_fortuneo,extract_quantity,compute_transactions_degiro,apply_id

from tools.tools import process_csv_incremental,log_added_rows,convert_prices_to_eur,compute_portfolio_value_from_prices_positions,append_df_to_csv,transac_to_portfolio,transac_to_df, date_stock,sav_int_prop,build_car_value_series
import plotly.express as px
import plotly.graph_objects as go

from tools.tools import my_debt
from tools.tools import transac_to_portfolio
from pathlib import Path

st.set_page_config(page_title="Income", layout="wide")

st.title("📊 Income")

# Load data from session state
@st.cache_data(show_spinner=False)
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

    return patrimoine, portfolio,df_all, all_balance,my_stock_evo,df_all


# if st.checkbox('load_data'):
patrimoine, portfolio, df_all,all_balance,my_stock_evo,my_inc_stock_tot = load_portfolio_data(datetime.datetime.today())
product_tickers_currency_plus = pd.read_csv('master_data/product_tickers_currency_plus.csv')
st.write('portfolio',portfolio)
st.write('patrimoine',patrimoine)
st.write('product_tickers_currency_plus',product_tickers_currency_plus)
my_div = pd.read_csv('master_data/dividend_list')
my_int = pd.read_csv('master_data/interest')

st.write('my_div',my_div)
st.write('my_int',my_int)

cur_port = pd.DataFrame(portfolio.iloc[len(portfolio)-1])
cur_port.rename(columns = {list(cur_port.columns)[0]: 'quantity'}, inplace = True)

cur_div=pd.merge(left=my_div,right=product_tickers_currency_plus,left_on='Product',right_on='product_name').drop_duplicates(subset='tickers')
cur_port=pd.merge(left=cur_port,right=cur_div,on='tickers')

st.write(cur_div)
st.write(cur_port)

stock_histo = pd.read_csv("master_data/stock_final2", usecols=["Date", "Close", "Tickers", "Currency"])
my_change = stock_histo[stock_histo['Tickers'].str.contains('USDEUR|GBP')].drop_duplicates(subset='Tickers',keep='last')
my_change['Tickers'] = my_change['Tickers'].apply(lambda x :'USD' if "USD" in x else 'GBp')
my_change.loc[my_change['Tickers'].str.contains('GBp'),'Close'] =my_change.loc[my_change['Tickers'].str.contains('GBp'),'Close']/100
st.write(my_change)
my_change=my_change[['Close','Tickers']].copy()
my_change=pd.concat([my_change,pd.DataFrame({'Close':[1],'Tickers':['EUR']})]).rename(columns={'Tickers':'currency'})
st.write(my_change)
my_div_df =pd.merge(left=cur_port, right=my_change,how='left',on='currency')
my_div_df['div_net'] = my_div_df['quantity']*my_div_df['Dividends']*my_div_df['Close']*my_div_df['Net']
st.write(my_div_df)
st.write(my_div_df.div_net.sum())

def style_portfolio(df):
    return (
        df
        .style
        .hide(axis="index")
        .format({
            "div_net": "{:,.2f}",
            "Close": "{:,.2f}",
            "quantity": "{:,.0f}"
        })
        .background_gradient(
            subset=["div_net"],
            cmap="Greens"
        )
        .set_properties(
            subset=["product_name"],
            **{"font-weight": "bold"}
        )
        .set_table_styles([
            # Header
            {
                "selector": "th",
                "props": [
                    ("font-weight", "bold"),
                    ("font-size", "14px"),
                    ("text-align", "center"),
                    ("background-color", "#f0f2f6")
                ]
            },
            # Cells
            {
                "selector": "td",
                "props": [
                    ("font-size", "13px"),
                    ("padding", "6px 10px")
                ]
            }
        ])
    )
df_view = my_div_df[my_div_df["quantity"] > 0].copy()
df_view.drop(columns=['Product','product_id','tickers_from','tickers_to'],inplace=True)

st.markdown(
    """
    <h2 style='margin-bottom: 0;'>📈 Dividend Portfolio Overview</h2>
    <p style='color: gray; margin-top: 4px;'>
    Holdings with positive quantity — rows shaded by net dividend contribution
    </p>
    """,
    unsafe_allow_html=True
)

st.dataframe(
    style_portfolio(df_view),
    use_container_width=True,
    height='content',
    hide_index=True
)

st.markdown(
    """
    <p style='font-size: 12px; color: gray;'>
    💡 <i>Gradient color reflects <b>div_net</b>: darker green = higher dividend contribution.</i>
    </p>
    """,
    unsafe_allow_html=True
)


df= patrimoine.copy()
exclude_cols = { 
                # "Mettlach-Wehingen",
                "total_debt",
                'stocks'}
value_cols = [c for c in df.columns if c not in exclude_cols]
df=df[value_cols].copy()
df=pd.DataFrame(df.iloc[len(df)-1].copy())
df.rename(columns={df.columns[0]:'value'},inplace=True)
df= df[df['value']>0]
st.write(df)

INTEREST_PATH = Path("master_data/interest")
@st.cache_data
def load_interest(path):
    return pd.read_csv(path)

interest_df = load_interest(INTEREST_PATH).set_index('Product')
st.write(interest_df)
df = pd.merge(left=df,right=interest_df,left_index=True,right_index=True)
df['int_eur'] = df['value']*df['Net']*df['Interest']
st.write(df)
int_saving = df.int_eur.sum()
st.write(int_saving)

my_income=(pd.concat(
    [
        df[['int_eur']].rename(columns={'int_eur':'amount'}),
        my_div_df[['product_name','div_net']].set_index('product_name').rename(columns={'div_net':'amount'})
        ]))

import pandas as pd

# Ensure numeric (handles empty strings / NaN)
my_income["amount"] = pd.to_numeric(my_income["amount"], errors="coerce")

# Split
below_100 = my_income[my_income["amount"] < 100]
above_100 = my_income[my_income["amount"] >= 100]

# Sum rows below 100
sum_below_100 = pd.DataFrame(
    {"amount": [below_100["amount"].sum()]},
    index=["sum_below_100"]
)

# Recombine
my_income= pd.concat([above_100, sum_below_100])
my_income = my_income.sort_values("amount", ascending=False)
my_income["amount"] = my_income["amount"].round(2)

st.write(my_income)
labels = my_income.index
values = my_income.amount
total_value = values.sum()

labels = [l for l, v in zip(labels, values) if v != 0]
values = [v for v in values if v != 0]
palette = px.colors.qualitative.Safe + px.colors.qualitative.Set2 + px.colors.qualitative.Pastel

color_map = {asset: palette[i % len(palette)] for i, asset in enumerate(my_income.index)}

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
    title=f"Income distribution",
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

st.write(my_inc_stock_tot['Dividende'])

my_div = pd.read_csv('master_data/transactions_master')
my_div = my_div[my_div['description']=='Dividende']
my_transac = pd.read_csv('master_data/transactions_master')

my_int = pd.read_csv('master_data/saving')
my_int.rename(columns =
    {
        'Date':'date',
        'Product':'product_name',
        'Total':'total',
        'Description':'description'
        
    },inplace=True
)
my_int = my_int[my_int['description']=='Interest']
st.write('my_int',my_int)
st.write('my_div',my_div)
st.write(pd.concat([
    my_int[['date','product_name','total','description']],
    my_div[['date','product_name','total','description']]
    ],axis=0))
my_transac_ac_ve = my_transac[my_transac['description'].str.contains('Achat|Vente')]
my_transac_ac_ve.rename(columns={'product_name':'product'},inplace=True)
my_transac_ac_ve['total'] = my_transac_ac_ve['total']*(-1)

st.write('my_transac',my_transac_ac_ve)

# my_saving = sav_int_prop('master_data/saving')
my_saving = pd.read_csv('master_data/saving')
st.write('my_saving',my_saving)
my_saving = my_saving[my_saving['Description']!='Interest']
my_saving.columns = [x.lower() for x in my_saving.columns] 
st.write('saving' , my_saving)
my_debt_df = my_debt()
my_debt_df['repayment'] = my_debt_df['total_debt'].shift()
my_debt_df['repayment'] = my_debt_df['repayment'].fillna(185000)
my_debt_df['repayment'] = my_debt_df['repayment'] - my_debt_df['total_debt']
my_debt_df['total'] = my_debt_df['repayment']
my_debt_df['description'] = 'Mortgage repayment'
my_debt_df['product'] = 'Appartment'
my_debt_df.reset_index(inplace=True)

st.write('my_debt_df' , my_debt_df)
col_to_keep =['date','description', 'product','total']
my_sav_fu = pd.concat([
    my_transac_ac_ve[col_to_keep],
    my_saving[col_to_keep],
    my_debt_df[col_to_keep]
])
my_sav_fu['date'] = pd.to_datetime(my_sav_fu['date'])
st.write('my_sav_fu' , my_sav_fu)
my_sav_fu2 = pd.DataFrame(my_sav_fu.resample('MS', on='date').sum()["total"]).reset_index()[1:]
st.write('my_sav_fu2',my_sav_fu2)
for i in [24]:
    my_sav_fu2["average_on_{}_months".format(i)] = my_sav_fu2["total"].rolling(
        i, min_periods=6).mean()

# fig = px.line(x=my_sav_fu2.Date.values, y=my_sav_fu2.moyenne_glissante.values, color=px.Constant("mean on {} months".format(x_months)))
fig = px.line(my_sav_fu2, x=my_sav_fu2.date.values, y=[
                x for x in my_sav_fu2.columns if "avera" in x],
              title = 'Savings follow-up')

fig.add_bar(x=my_sav_fu2.date, y=my_sav_fu2.total,
            name="saving per month", marker_color="grey")
# st.plotly_chart(fig, use_container_width=True)

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# -------------------------
# Prepare data
# -------------------------
col_to_keep = ['date', 'description', 'product', 'total']

df = pd.concat([
    my_transac_ac_ve[col_to_keep],
    my_saving[col_to_keep],
    my_debt_df[col_to_keep]
]).copy()

df['date'] = pd.to_datetime(df['date'])

# Monthly aggregation
monthly = (
    df
    .set_index('date')
    .resample('MS')['total']
    .sum()
    .reset_index()
)

monthly['avg_24m'] = monthly['total'].rolling(24, min_periods=6).mean()

# -------------------------
# Plot
# -------------------------
fig = go.Figure()

fig.add_trace(go.Bar(
    x=monthly['date'],
    y=monthly['total'],
    name="saving per month",
    marker_color="grey"
))

fig.add_trace(go.Scatter(
    x=monthly['date'],
    y=monthly['avg_24m'],
    mode='lines',
    name="average_on_24_months",
    line=dict(color='blue')
))

fig.update_layout(
    title="Savings follow-up",
    hovermode="x unified"
)

# -------------------------
# 👉 Native Streamlit selection
# -------------------------
event = st.plotly_chart(
    fig,
    use_container_width=True,
    on_select="rerun",
    selection_mode="points"
)

# -------------------------
# Handle click
# -------------------------
if event and "selection" in event and event["selection"]["points"]:
    point = event["selection"]["points"][0]

    clicked_date = pd.to_datetime(point["x"])

    df_month = df[
        (df['date'].dt.year == clicked_date.year) &
        (df['date'].dt.month == clicked_date.month)
    ].copy()

    # Nice formatting
    df_month['date'] = df_month['date'].dt.strftime('%Y-%m-%d')
    df_month['total'] = df_month['total'].map("{:,.2f} €".format)

    st.subheader(f"Details for {clicked_date.strftime('%B %Y')}")
    st.dataframe(df_month, use_container_width=True)
import streamlit as st
import pandas as pd
import numpy as np
import os
import sys
import shutil
from tempfile import NamedTemporaryFile

p = os.path.abspath('../..')
if p not in sys.path:
    sys.path.append(p)

from tools.tools import process_csv_incremental,log_added_rows,append_df_to_csv
# os.chdir()


# --------------------------------------------------
# ⚙️ PAGE CONFIG
# --------------------------------------------------
st.set_page_config(page_title="Portfolio Data Manager", layout="wide")

st.title("📊 Portfolio Data Manager")
st.markdown(
    """
    This page lets you **import transactions**, and maintain all the reference tables  
    used across your portfolio dashboard:
    - 💰 Savings history  
    - 📈 Interest rates  
    - 💵 Dividend reference data  
    - 🏷️ Product ↔ Ticker mappings  
    """
)
st.divider()

# --------------------------------------------------
# 📥 TRANSACTION FILE PROCESSING
# --------------------------------------------------
st.header("📥 Import Bank Statements")


deg_file_to_process = st.pills("Select the files to process:",
    
    [x.split('.')[0] for x in [x for x in os.listdir('bank_statements') if 'DEG' in x][-10:]],selection_mode='multi')
fort_file_to_process = st.pills("Select the files to process:",
    
    [x.split('.')[0] for x in [x for x in os.listdir('bank_statements') if 'FORT' in x][-10:]],selection_mode='multi')


# fort_file_to_process = [x.split('.')[0] for x in [x for x in os.listdir('../bank_statements') if 'FORT' in x][-10:]]
files_to_process = fort_file_to_process+deg_file_to_process
if st.button('Process the files'):
    for file_name in files_to_process:
        st.write(file_name)
        transactions_m =pd.read_csv('master_data/transactions_master')
        added = process_csv_incremental(file_name, transactions_m)
        log_added_rows(added, file_name)
        st.write(append_df_to_csv('master_data/transactions_master', added))
        
import streamlit as st
import pandas as pd
from pathlib import Path

st.divider()

# ---------- Config ----------
# st.set_page_config(page_title="Savings Tracker", layout="wide")

DATA_PATH = Path("master_data/saving")

# ---------- Load data ----------
@st.cache_data
def load_data(path):
    df = pd.read_csv(path, parse_dates=["Date"])
    return df

df = load_data(DATA_PATH)

st.header("💰 Savings Follow-Up")

# ---------- Editable table ----------
# st.subheader("📋 Edit Savings Data")

# Session state to hold working dataframe
if "working_df" not in st.session_state:
    st.session_state.working_df = df.copy()

# ---- Button to show add-row form ----
if "show_add_row" not in st.session_state:
    st.session_state.show_add_row = False

if st.button("➕ Add new row"):
    st.session_state.show_add_row = True

# ---- Add row form (appears only when button clicked) ----
if st.session_state.show_add_row:
    with st.container(border=True):
        # st.markdown("### New Entry")

        col1, col2, col3 = st.columns(3)

        with col1:
            new_date = st.date_input("Date", key="new_date")
            # new_product = st.text_input("Product", key="new_product")

            existing_products = sorted(st.session_state.working_df["Product"].dropna().unique())

            product_mode = st.radio(
                "Product source",
                ["Select existing", "Add new"],
                horizontal=True
            )

            if product_mode == "Select existing":
                new_product = st.selectbox("Product", existing_products)
            else:
                new_product = st.text_input("New product name")

        with col2:
            new_total = st.number_input("Total", step=100.0, key="new_total")
            new_currency = st.selectbox("Currency", ["EUR", "USD", "CHF"], key="new_currency")

        with col3:
            new_description = st.selectbox(
                "Description",
                ["Saving", "Interest", "Withdrawal", "Other"],
                key="new_description"
            )

        col_add, col_cancel = st.columns(2)

        if col_add.button("✅ Add to table"):
            new_row = pd.DataFrame([{
                "Date": pd.to_datetime(new_date),
                "Product": new_product,
                "Total": new_total,
                "Description": new_description,
                "Currency": new_currency,
            }])

            st.session_state.working_df = pd.concat(
                [st.session_state.working_df, new_row],
                ignore_index=True
            )

            st.success("Row added at bottom 👇")
            st.session_state.show_add_row = False
            st.rerun()

        if col_cancel.button("❌ Cancel"):
            st.session_state.show_add_row = False
            st.rerun()

# ---- Data editor (editing only) ----
edited_df = st.data_editor(
    st.session_state.working_df,
    num_rows="dynamic",   # prevent adding inside table
    use_container_width=True
)

st.session_state.working_df = edited_df

# ---- Save button ----
if st.button("💾 Save changes"):
    st.session_state.working_df.to_csv(DATA_PATH, index=False)
    st.success("File saved successfully!")
    st.cache_data.clear()

st.divider()

INTEREST_PATH = Path("master_data/interest")
@st.cache_data
def load_interest(path):
    return pd.read_csv(path)

interest_df = load_interest(INTEREST_PATH)

st.header("📈 Interest Rates by Product")
# st.subheader("📋 Edit Interest Table")

if "interest_working_df" not in st.session_state:
    st.session_state.interest_working_df = interest_df.copy()

edited_interest_df = st.data_editor(
    st.session_state.interest_working_df,
    num_rows="dynamic",
    use_container_width=True,
    key="interest_editor"
)

st.session_state.interest_working_df = edited_interest_df
# st.subheader("➕ Add New Product")

with st.form("add_interest_form", clear_on_submit=True):
    col1, col2, col3 = st.columns(3)

    with col1:
        new_product = st.text_input("Product name")

    with col2:
        new_interest = st.number_input("Interest rate", step=0.001, format="%.4f")

    with col3:
        new_net = st.number_input("Net factor", step=0.01, value=1.0)

    submitted = st.form_submit_button("Add product")

    if submitted:
        new_row = pd.DataFrame([{
            "Product": new_product,
            "Interest": new_interest,
            "Net": new_net
        }])

        st.session_state.interest_working_df = pd.concat(
            [st.session_state.interest_working_df, new_row],
            ignore_index=True
        )

        st.success("Product added ✅")
        st.rerun()

if st.button("💾 Save Interest Table"):
    st.session_state.interest_working_df.to_csv(INTEREST_PATH, index=False)
    st.success("Interest file saved!")
    st.cache_data.clear()
st.divider()

st.header("💰 Dividend Reference")

DIVIDEND_PATH = "master_data/dividend_list"

# ---------- Load once ----------
@st.cache_data
def load_dividend_data(path):
    return pd.read_csv(path)

div_df = load_dividend_data(DIVIDEND_PATH)

# ---------- Session state ----------
if "div_working_df" not in st.session_state:
    st.session_state.div_working_df = div_df.copy()

if "show_add_div_row" not in st.session_state:
    st.session_state.show_add_div_row = False

# ---------- Add button ----------
if st.button("➕ Add new dividend entry"):
    st.session_state.show_add_div_row = True

# ---------- Add row form ----------
if st.session_state.show_add_div_row:
    with st.container(border=True):
        # st.markdown("### New Dividend Entry")

        col1, col2, col3 = st.columns(3)

        with col1:
            new_product = st.text_input("Product name")

        with col2:
            new_dividend = st.number_input(
                "Annual Dividend",
                min_value=0.0,
                step=0.1,
                format="%.4f"
            )

        with col3:
            new_net = st.number_input(
                "Net factor",
                min_value=0.0,
                max_value=1.0,
                step=0.01,
                format="%.3f",
                help="Multiplier after tax (ex: 0.85 = 15% tax)"
            )

        col_add, col_cancel = st.columns(2)

        if col_add.button("✅ Add to table",key=98):
            if new_product.strip() == "":
                st.warning("Product name cannot be empty")
            else:
                new_row = pd.DataFrame([{
                    "Product": new_product.strip(),
                    "Dividends": new_dividend,
                    "Net": new_net,
                }])

                st.session_state.div_working_df = pd.concat(
                    [st.session_state.div_working_df, new_row],
                    ignore_index=True
                )

                st.success("Dividend entry added 👇")
                st.session_state.show_add_div_row = False
                st.rerun()

        if col_cancel.button("❌ Cancel",key=0):
            st.session_state.show_add_div_row = False
            st.rerun()

# ---------- Data editor ----------
edited_div_df = st.data_editor(
    st.session_state.div_working_df,
    num_rows="dynamic",
    use_container_width=True,
    column_config={
        "Product": st.column_config.TextColumn("Product"),
        "Dividends": st.column_config.NumberColumn("Dividends", format="%.4f"),
        "Net": st.column_config.NumberColumn("Net", format="%.3f"),
    }
)

st.session_state.div_working_df = edited_div_df

# ---------- Save ----------
if st.button("💾 Save dividend list"):
    st.session_state.div_working_df.to_csv(DIVIDEND_PATH, index=False)
    st.success("Dividend file saved successfully!")
    st.cache_data.clear()

st.divider()
st.header("🏷️ Product–Ticker Mapping")

TICKER_PATH = "master_data/product_tickers_currency_plus.csv"

# ---------- Load ----------
@st.cache_data
def load_ticker_data(path):
    df = pd.read_csv(path, parse_dates=["tickers_from", "tickers_to"])
    return df

ticker_df = load_ticker_data(TICKER_PATH)

# ---------- Session state ----------
if "ticker_working_df" not in st.session_state:
    st.session_state.ticker_working_df = ticker_df.copy()

if "show_add_ticker_row" not in st.session_state:
    st.session_state.show_add_ticker_row = False

# ---------- Add button ----------
if st.button("➕ Add new product–ticker link"):
    st.session_state.show_add_ticker_row = True

# ---------- Add row form ----------
if st.session_state.show_add_ticker_row:
    with st.container(border=True):
        st.markdown("### New Mapping Entry")

        col1, col2, col3 = st.columns(3)

        with col1:
            new_product_name = st.text_input("Product name")
            new_product_id = st.text_input(
                "Product ID (canonical name)",
                help="Used to group multiple ticker histories under one product"
            )

        with col2:
            new_ticker = st.text_input("Ticker symbol")
            new_currency = st.selectbox(
                "Currency",
                ["EUR", "USD", "GBp", "CHF", "SEK", "PLN", "Other"]
            )

        with col3:
            new_from = st.date_input("Valid from")
            new_to = st.date_input("Valid to", value=pd.Timestamp("2100-01-01"))

        col_add, col_cancel = st.columns(2)

        if col_add.button("✅ Add mapping"):
            if not new_product_name or not new_ticker:
                st.warning("Product name and ticker are required")
            else:
                new_row = pd.DataFrame([{
                    "product_name": new_product_name.strip(),
                    "tickers": new_ticker.strip(),
                    "currency": new_currency,
                    "product_id": new_product_id.strip() if new_product_id else new_product_name.strip(),
                    "tickers_from": pd.to_datetime(new_from),
                    "tickers_to": pd.to_datetime(new_to),
                }])

                st.session_state.ticker_working_df = pd.concat(
                    [st.session_state.ticker_working_df, new_row],
                    ignore_index=True
                )

                st.success("Mapping added 👇")
                st.session_state.show_add_ticker_row = False
                st.rerun()

        if col_cancel.button("❌ Cancel"):
            st.session_state.show_add_ticker_row = False
            st.rerun()

# ---------- Optional filter ----------
filter_product = st.text_input("🔍 Filter by product or ticker")

display_df = st.session_state.ticker_working_df
if filter_product:
    mask = (
        display_df["product_name"].str.contains(filter_product, case=False, na=False) |
        display_df["tickers"].str.contains(filter_product, case=False, na=False) |
        display_df["product_id"].str.contains(filter_product, case=False, na=False)
    )
    display_df = display_df[mask]

# ---------- Editor ----------
edited_ticker_df = st.data_editor(
    display_df,
    use_container_width=True,
    num_rows="dynamic",
    column_config={
        "product_name": st.column_config.TextColumn("Product Name"),
        "tickers": st.column_config.TextColumn("Ticker"),
        "currency": st.column_config.SelectboxColumn(
            "Currency",
            options=["EUR", "USD", "GBp", "CHF", "SEK", "PLN", "Other"]
        ),
        "product_id": st.column_config.TextColumn("Product ID"),
        "tickers_from": st.column_config.DateColumn("Valid From"),
        "tickers_to": st.column_config.DateColumn("Valid To"),
    }
)

# Merge edits back into full dataset when filtering is active
if filter_product:
    full_df = st.session_state.ticker_working_df.copy()
    full_df.update(edited_ticker_df)
    st.session_state.ticker_working_df = full_df
else:
    st.session_state.ticker_working_df = edited_ticker_df

# ---------- Save ----------
if st.button("💾 Save ticker mappings"):
    st.session_state.ticker_working_df = (
        st.session_state.ticker_working_df
        .sort_values(["product_id", "tickers_from"])
        .reset_index(drop=True)
    )

    st.session_state.ticker_working_df.to_csv(TICKER_PATH, index=False)
    st.success("Ticker mapping file saved!")
    st.cache_data.clear()

st.divider()

# import streamlit as st
# import pandas as pd
# import numpy as np
# import os
# import sys
# from pathlib import Path

# # --------------------------------------------------
# # ⚙️ PAGE CONFIG
# # --------------------------------------------------
# st.set_page_config(page_title="Portfolio Data Manager", layout="wide")

# st.title("📊 Portfolio Data Manager")
# st.markdown(
#     """
#     This page lets you **import transactions**, and maintain all the reference tables  
#     used across your portfolio dashboard:
#     - 💰 Savings history  
#     - 📈 Interest rates  
#     - 💵 Dividend reference data  
#     - 🏷️ Product ↔ Ticker mappings  
#     """
# )
# st.divider()

# # --------------------------------------------------
# # 📥 TRANSACTION FILE PROCESSING
# # --------------------------------------------------
# st.header("📥 Import Bank Statements")

# deg_file_to_process = st.pills(
#     "Select DEG files",
#     [x.split('.')[0] for x in os.listdir('bank_statements') if 'DEG' in x][-10:],
#     selection_mode='multi'
# )

# fort_file_to_process = st.pills(
#     "Select FORT files",
#     [x.split('.')[0] for x in os.listdir('bank_statements') if 'FORT' in x][-10:],
#     selection_mode='multi'
# )

# files_to_process = fort_file_to_process + deg_file_to_process

# if st.button('🚀 Process selected files', key="process_files"):
#     from tools.tools import process_csv_incremental, log_added_rows, append_df_to_csv
#     transactions_m = pd.read_csv('master_data/transactions_master')

#     for file_name in files_to_process:
#         st.write(f"Processing {file_name}...")
#         added = process_csv_incremental(file_name, transactions_m)
#         log_added_rows(added, file_name)
#         append_df_to_csv('master_data/transactions_master', added)

#     st.success("Processing complete!")

# st.divider()

# # --------------------------------------------------
# # 💰 SAVINGS DATA
# # --------------------------------------------------
# st.header("💰 Savings History")

# DATA_PATH = Path("master_data/saving")

# @st.cache_data
# def load_data(path):
#     return pd.read_csv(path, parse_dates=["Date"])

# df = load_data(DATA_PATH)

# if "working_df" not in st.session_state:
#     st.session_state.working_df = df.copy()

# if "show_add_row" not in st.session_state:
#     st.session_state.show_add_row = False

# st.subheader("📋 Edit Table")

# if st.button("➕ Add new savings row", key="show_add_savings"):
#     st.session_state.show_add_row = True

# if st.session_state.show_add_row:
#     with st.container(border=True):
#         st.markdown("### New Savings Entry")
#         col1, col2, col3 = st.columns(3)

#         with col1:
#             new_date = st.date_input("Date", key="new_date")
#             existing_products = sorted(st.session_state.working_df["Product"].dropna().unique())
#             product_mode = st.radio("Product source", ["Select existing", "Add new"], horizontal=True, key="savings_product_mode")
#             new_product = st.selectbox("Product", existing_products, key="existing_product") if product_mode == "Select existing" else st.text_input("New product name", key="new_product_name")

#         with col2:
#             new_total = st.number_input("Total", step=100.0, key="new_total")
#             new_currency = st.selectbox("Currency", ["EUR", "USD", "CHF"], key="new_currency")

#         with col3:
#             new_description = st.selectbox("Description", ["Saving", "Interest", "Withdrawal", "Other"], key="new_description")

#         c1, c2 = st.columns(2)
#         if c1.button("✅ Add to table", key="add_savings_row"):
#             new_row = pd.DataFrame([{
#                 "Date": pd.to_datetime(new_date),
#                 "Product": new_product,
#                 "Total": new_total,
#                 "Description": new_description,
#                 "Currency": new_currency,
#             }])
#             st.session_state.working_df = pd.concat([st.session_state.working_df, new_row], ignore_index=True)
#             st.session_state.show_add_row = False
#             st.rerun()

#         if c2.button("❌ Cancel", key="cancel_savings_row"):
#             st.session_state.show_add_row = False
#             st.rerun()

# edited_df = st.data_editor(st.session_state.working_df, num_rows="dynamic", use_container_width=True)
# st.session_state.working_df = edited_df

# if st.button("💾 Save savings data", key="save_savings"):
#     st.session_state.working_df.to_csv(DATA_PATH, index=False)
#     st.success("Savings file saved!")
#     st.cache_data.clear()

# st.divider()

# # --------------------------------------------------
# # 📈 INTEREST TABLE
# # --------------------------------------------------
# st.header("📈 Interest Rates")

# INTEREST_PATH = Path("master_data/interest")

# @st.cache_data
# def load_interest(path):
#     return pd.read_csv(path)

# interest_df = load_interest(INTEREST_PATH)

# if "interest_working_df" not in st.session_state:
#     st.session_state.interest_working_df = interest_df.copy()

# edited_interest_df = st.data_editor(
#     st.session_state.interest_working_df,
#     num_rows="dynamic",
#     use_container_width=True,
#     key="interest_editor"
# )

# st.session_state.interest_working_df = edited_interest_df

# with st.form("add_interest_form", clear_on_submit=True):
#     st.subheader("➕ Add New Product")
#     col1, col2, col3 = st.columns(3)
#     new_product = col1.text_input("Product name")
#     new_interest = col2.number_input("Interest rate", step=0.001, format="%.4f")
#     new_net = col3.number_input("Net factor", step=0.01, value=1.0)

#     if st.form_submit_button("Add product", key="add_interest_product"):
#         new_row = pd.DataFrame([{"Product": new_product, "Interest": new_interest, "Net": new_net}])
#         st.session_state.interest_working_df = pd.concat([st.session_state.interest_working_df, new_row], ignore_index=True)
#         st.rerun()

# if st.button("💾 Save interest table", key="save_interest"):
#     st.session_state.interest_working_df.to_csv(INTEREST_PATH, index=False)
#     st.success("Interest file saved!")
#     st.cache_data.clear()

# st.divider()

# # --------------------------------------------------
# # 💵 DIVIDEND TABLE
# # --------------------------------------------------
# st.header("💵 Dividend Reference")

# DIVIDEND_PATH = "master_data/dividend_list"

# @st.cache_data
# def load_dividend_data(path):
#     return pd.read_csv(path)

# div_df = load_dividend_data(DIVIDEND_PATH)

# if "div_working_df" not in st.session_state:
#     st.session_state.div_working_df = div_df.copy()

# if "show_add_div_row" not in st.session_state:
#     st.session_state.show_add_div_row = False

# if st.button("➕ Add new dividend entry", key="show_add_dividend"):
#     st.session_state.show_add_div_row = True

# if st.session_state.show_add_div_row:
#     with st.container(border=True):
#         st.markdown("### New Dividend Entry")
#         col1, col2, col3 = st.columns(3)

#         new_product = col1.text_input("Product name")
#         new_dividend = col2.number_input("Annual Dividend", min_value=0.0, step=0.1, format="%.4f")
#         new_net = col3.number_input("Net factor", min_value=0.0, max_value=1.0, step=0.01, format="%.3f")

#         c1, c2 = st.columns(2)
#         if c1.button("✅ Add to table", key="add_dividend_row"):
#             new_row = pd.DataFrame([{"Product": new_product, "Dividends": new_dividend, "Net": new_net}])
#             st.session_state.div_working_df = pd.concat([st.session_state.div_working_df, new_row], ignore_index=True)
#             st.session_state.show_add_div_row = False
#             st.rerun()

#         if c2.button("❌ Cancel", key="cancel_dividend_row"):
#             st.session_state.show_add_div_row = False
#             st.rerun()

# edited_div_df = st.data_editor(st.session_state.div_working_df, use_container_width=True)
# st.session_state.div_working_df = edited_div_df

# if st.button("💾 Save dividend list", key="save_dividends"):
#     st.session_state.div_working_df.to_csv(DIVIDEND_PATH, index=False)
#     st.success("Dividend file saved!")
#     st.cache_data.clear()

# st.divider()

# # --------------------------------------------------
# # 🏷️ PRODUCT ↔ TICKER MAPPING
# # --------------------------------------------------
# st.header("🏷️ Product–Ticker Mapping")

# TICKER_PATH = "master_data/product_tickers_currency_plus.csv"

# @st.cache_data
# def load_ticker_data(path):
#     return pd.read_csv(path, parse_dates=["tickers_from", "tickers_to"])

# ticker_df = load_ticker_data(TICKER_PATH)

# if "ticker_working_df" not in st.session_state:
#     st.session_state.ticker_working_df = ticker_df.copy()

# if "show_add_ticker_row" not in st.session_state:
#     st.session_state.show_add_ticker_row = False

# if st.button("➕ Add new mapping", key="show_add_ticker"):
#     st.session_state.show_add_ticker_row = True

# if st.session_state.show_add_ticker_row:
#     with st.container(border=True):
#         st.markdown("### New Mapping Entry")
#         col1, col2, col3 = st.columns(3)

#         new_product_name = col1.text_input("Product name")
#         new_product_id = col1.text_input("Product ID (canonical)")
#         new_ticker = col2.text_input("Ticker symbol")
#         new_currency = col2.selectbox("Currency", ["EUR", "USD", "GBp", "CHF", "SEK", "PLN", "Other"])
#         new_from = col3.date_input("Valid from")
#         new_to = col3.date_input("Valid to", value=pd.Timestamp("2100-01-01"))

#         c1, c2 = st.columns(2)
#         if c1.button("✅ Add mapping", key="add_ticker_row"):
#             new_row = pd.DataFrame([{
#                 "product_name": new_product_name,
#                 "tickers": new_ticker,
#                 "currency": new_currency,
#                 "product_id": new_product_id or new_product_name,
#                 "tickers_from": pd.to_datetime(new_from),
#                 "tickers_to": pd.to_datetime(new_to),
#             }])
#             st.session_state.ticker_working_df = pd.concat([st.session_state.ticker_working_df, new_row], ignore_index=True)
#             st.session_state.show_add_ticker_row = False
#             st.rerun()

#         if c2.button("❌ Cancel", key="cancel_ticker_row"):
#             st.session_state.show_add_ticker_row = False
#             st.rerun()

# filter_product = st.text_input("🔍 Filter product or ticker")
# display_df = st.session_state.ticker_working_df
# if filter_product:
#     mask = display_df.apply(lambda r: r.astype(str).str.contains(filter_product, case=False).any(), axis=1)
#     display_df = display_df[mask]

# edited_ticker_df = st.data_editor(display_df, use_container_width=True)
# st.session_state.ticker_working_df.update(edited_ticker_df)

# if st.button("💾 Save ticker mappings", key="save_tickers"):
#     st.session_state.ticker_working_df.to_csv(TICKER_PATH, index=False)
#     st.success("Ticker mappings saved!")
#     st.cache_data.clear()

# st.divider()
# st.caption("✅ All portfolio reference data managed in one place")

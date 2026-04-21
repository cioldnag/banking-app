# =============================================
# Portfolio processing pipeline (refactored)
# SAME OUTPUT – CLEAN ARCHITECTURE
# =============================================

import os
import timeit
import numpy as np
import pandas as pd
import streamlit as st
import pandas as pd
from random import randint
from tempfile import NamedTemporaryFile
import shutil
import re

# =============================================
# Utils
# =============================================


from datetime import datetime
from dateutil.relativedelta import relativedelta
# from tools.tools import latest_csv
pd.options.display.max_rows=100
from datetime import date

def normalize_date(df, col):
    df[col] = pd.to_datetime(df[col], dayfirst=True)
    return df

def normalize_decimal(df, cols):
    for c in cols:
        df[c] = (
            df[c]
            .astype(str)
            .str.replace(",", ".", regex=False)
            .astype(float)
        )
    return df

def latest_fortuneo(path="bank_statements",file_back=-1):
    data_fortuneo = pd.read_csv(path +"/" +sorted([i for i in os.listdir(
        path) if "FORTUNEO" in i])[file_back], encoding="ISO-8859-1", delimiter=";")
    return data_fortuneo

def latest_degiro(path="bank_statements",file_back=-1):   
    data_degiro = pd.read_csv(
        path +"/" + sorted([i for i in os.listdir(path) if "DEGIRO" in i])[file_back])
    return data_degiro

def load_base_history():
    data = pd.read_csv('stock_processed/'+sorted([i for i in os.listdir('stock_processed') if (("-" in i) and i[0]=='2' )])[-1])
    # st.write(sorted([i for i in os.listdir() if (("-" in i) and i[0]=='2' )]))
    data.drop("Unnamed: 0", axis=1, inplace=True)
    data.sort_values(by="Date", inplace=True)
    data.drop(columns=["Unnamed: 0"], errors="ignore", inplace=True)
    data = normalize_date(data, "Date")
    data.sort_values("Date", inplace=True)
    return data

def merge_w_tickers(my_data_stock: pd.DataFrame)->pd.DataFrame:
    my_map_ti = pd.read_csv('master_data/product_tickers_currency_plus.csv',sep=',')
    my_map_ti.rename(columns={
        'Product':'product_name',
        'Tickers':'tickers',
        'Currency':'currency'
        
    },inplace=True)
    my_map_ti = my_map_ti[['product_name','tickers']].copy()
    res = pd.merge(left=my_data_stock,right = my_map_ti,on= 'product_name',how='left')
    return res

def normalize_degiro(df):
    df = df.rename(columns={
        "Unnamed: 8": "amount",
        "Unnamed: 10": "balance",
        "Beschreibung": "description",
        "Saldo": "currency",
        "Produkt": "product_name",
        "FX": "fx",
        "ISIN":"isin",
        "Order-ID":'order_id','Datum':"date"
    })

    df = normalize_decimal(df, ["amount", "balance", "fx"])
    df = normalize_date(df, "date")
    my_renamer = pd.read_csv('master_data/product_tickers_currency_plus.csv')
    my_renamer =dict(zip(my_renamer["product_name"], my_renamer["product_id"]))
    df["product_name"] = df["product_name"].map(my_renamer).fillna(df["product_name"])
    df = df[[
        "date", "product_name", "isin", "description",
        "fx", "amount", "currency", "order_id"
    ]]

    return df.copy()

def normalize_fortuneo(df):
    df = df.rename(columns={
        "Montant net": "amount",
        "libellé": "product_name",
        "Date":"date",
        'Opération':'operation',
        'Place':'place',
        'Qté':'quantity',
        "Prix d'éxé":'price',
        "Courtage/Prélèvement":"courtage_prelevement",
        'Montant brut':'montant_brut',
        'Devise':'devise'
    })
    df = normalize_date(df, "date")
    my_renamer = pd.read_csv('master_data/product_tickers_currency_plus.csv')
    my_renamer =dict(zip(my_renamer["product_name"], my_renamer["product_id"]))
    df["product_name"] = df["product_name"].map(my_renamer).fillna(df["product_name"])
    df = df.loc[:, ~df.columns.duplicated()]
    return df

import pandas as pd

def compute_dividends_degiro(data_degiro):
    data = data_degiro.copy().reset_index(drop=True)
    
    mask_description = {
        'ividende':'Dividende',
        'gleich':'Barausgleich',
        'ckzahlung':'Kapitalrückzahlung'
        } 
    

    def map_description(text):
        for key, value in mask_description.items():
            if pd.notna(text) and key.lower() in text.lower():
                return value
        return None  # or 'Other'

    data['description_mask'] = data['description'].apply(map_description)

    # 1) Garder uniquement dividendes + taxes (exclure Kapitalrückzahlung)
    mask_div = (
        (data["description"] == "Dividende") |
        (data["description"].str.contains('gleich', na=False)) |
        (data["description"].str.contains("Dividendensteuer", na=False))|
        (data["description"].str.contains("Kapitalrückzahlung", na=False))        
    )

    # mask_no_capital = data["description"].str.contains(
    #     "Kapitalrückzahlung", na=False
    # )

    # data_div = data[mask_div & mask_no_capital].copy()

    data_div = data[mask_div].copy()

    # 2) Grouper par Date / product_name / currency
    grouped = (
        data_div
        .groupby(["date", "product_name", "currency",'description_mask'], as_index=False)
        .agg({"amount": "sum"})
    )

    # 3) Fonction interne pour trouver le fx
    def find_fx(idx, currency):
        if currency == "EUR":
            return 1.0

        for x in range(idx, max(idx - 20, -1), -1):
            if (
                data.loc[x, "description"] == "Währungswechsel (Ausbuchung)"
                and data.loc[x, "currency"] == currency
                and pd.notna(data.loc[x, "fx"])
                and data.loc[x, "fx"] > 0
            ):
                return data.loc[x, "fx"]

        return 1.0

    # 4) Conversion en EUR
    amounts_eur = []
    # display(grouped.head(5))
    for _, row in grouped.iterrows():
        data['date'] = pd.to_datetime(data['date'])

        # print(type(row.date),type(data["date"].values[-1]))
        # print(row.date,data["date"].values[-1] )
        # print(row.currency)
        idx = data.index[
            (data["date"] == row.date) &
            (data["product_name"] == row.product_name)
        ]
        # display(idx)
        idx=idx[0]

        fx = find_fx(idx, row.currency)
        amounts_eur.append(round(row.amount / fx, 2))

    grouped["amount"] = amounts_eur

    # # 5) Génération id_dividende (PATCH UNIQUEMENT)
    # def build_base_id(row):
    #     # date YYYYMMDD
    #     date_str = pd.to_datetime(row["date"]).strftime("%Y%m%d")

    #     # product_name: 25 chars, NO SPACE
    #     product_name = str(row["product_name"]).replace(" ", "").replace(".", "")
    #     product_name = product_name[:25].ljust(25, "X")

    #     # amount: largeur fixe, NO SPACE
    #     sign = "-" if row["amount"] < 0 else ""
    #     abs_amount = abs(row["amount"])
    #     amount_str = f"{abs_amount:08.2f}".replace(".", "_")
    #     amount_str = sign + amount_str

    #     return f"{date_str}{product_name}{amount_str}"

    # grouped["base_id"] = grouped.apply(build_base_id, axis=1)

    # grouped["id_dividende"] = (
    #     grouped
    #     .groupby("base_id")
    #     .cumcount()
    #     .astype(str)
    #     + grouped["base_id"]
    # )

    # 6) Table finale (inchangée + id)
    table_div = grouped[["date", "product_name", "amount",
                        #  "id_dividende",
                         'description_mask']]
    table_div=table_div.rename(columns={'description_mask':'description','id_dividende':'id','amount':'total'})
    table_div[['price', 'quantity', 'taxes', 'amount']] =np.nan

    table_div['broker'] = 'degiro'
    return table_div


import pandas as pd

def compute_dividends_fortuneo(fortuneo):

    df = fortuneo[
        fortuneo["operation"].str.contains("ncai", na=False) &
        fortuneo["place"].str.contains("aris|Amst", regex=True, na=False)
    ][["date", "product_name", "amount"]].copy()

    # 🚨 CAS CRITIQUE : aucun dividende
    if df.empty:
        return pd.DataFrame({
    "date": pd.Series(dtype="datetime64[ns]"),
    "product_name": pd.Series(dtype="object"),
    "total": pd.Series(dtype="float"),
    # "id_dividende": pd.Series(dtype="object"),
})


    # -------------------------------------------------
    # Génération id_dividende (MÊME LOGIQUE QUE DEGIRO)
    # -------------------------------------------------
    # def build_base_id(row):
    #     # date → YYYYMMDD
    #     date_str = pd.to_datetime(row["date"]).strftime("%Y%m%d")

    #     # product_name → 25 chars, uppercase, no space, pad X
    #     product_name = (
    #         str(row["product_name"])
    #         .upper()
    #         .replace(" ", "")
    #         .replace(".", "")
    #         .replace(",", "")
    #         .ljust(25, "X")[:25]
    #     )

    #     # amount → fixed width (00014_21)
    #     amount = round(abs(float(row["amount"])), 2)
    #     integer, decimal = f"{amount:.2f}".split(".")
    #     amount_str = f"{int(integer):05d}_{decimal}"

    #     if float(row["amount"]) < 0:
    #         amount_str = "-" + amount_str

    #     return f"{date_str}{product_name}{amount_str}"

    # # Base id
    # df["base_id"] = df.apply(build_base_id, axis=1)

    # # Doublons infinis → 0,1,2,...
    # df["id"] = (
    #     df.groupby("base_id")
    #       .cumcount()
    #       .astype(str)
    #       + df["base_id"]
    # )
    df['description']='Dividende'
    df['broker'] = 'fortuneo'
    df=df.rename(columns={'amount':'total'})
    df[['price', 'quantity', 'taxes', 'amount']] =np.nan
    return df[["date", "product_name", "total",
            #    "id",
               'description','broker','price', 'quantity', 'taxes', 'amount']]

import pandas as pd

def compute_transactions_fortuneo(fortuneo: pd.DataFrame) -> pd.DataFrame:
    df = fortuneo.copy()

    # --- Identify trades ---
    trades = df[df["operation"].str.contains("Achat|Vente", na=False)].copy()

    # --- Identify taxes ---
    taxes = df[df["operation"].str.contains("TAXE TRANSAC FINAN", na=False)].copy()
    # --- Normalize keys for merge ---
    for d in (trades, taxes):
        d["date"] = pd.to_datetime(d["date"])
        d["product_name_key"] = d["product_name"].str.upper().str[:25]
        d["quantity"] = d["quantity"].astype(float)

    # --- Aggregate taxes ---
    taxes_agg = (
        taxes.groupby(["date", "product_name_key", "quantity"], as_index=False)["amount"]
        .sum()
        .rename(columns={"amount": "taxe_ttf"})
    )

    # --- Merge taxes into trades ---
    trades = trades.merge(
        taxes_agg,
        on=["date", "product_name_key", "quantity"],
        how="left"
    )

    trades["taxe_ttf"] = trades["taxe_ttf"].fillna(0.0)

    # --- Transaction type & signed quantity ---
    trades["description"] = trades["operation"].apply(
        lambda x: "Vente" if "Vente" in x else "Achat"
    )

    trades["quantity"] = trades.apply(
        lambda r: -r["quantity"] if r["description"] == "Vente" else r["quantity"],
        axis=1
    )

    # --- Net amounts ---
    trades["amount"] = trades["montant_brut"] 
    trades['taxes'] = trades["taxe_ttf"] +trades["courtage_prelevement"]
    trades['total'] = trades['taxes'] + trades["amount"] 

    # --- ID components ---
    # trades["date_id"] = trades["date"].dt.strftime("%Y%m%d")

    # trades["product_name_id"] = (
    #     trades["product_name"]
    #     .str.upper()
    #     .str.replace(r"[^A-Z0-9]", "", regex=True)
    #     .str.ljust(25, "X")
    #     .str[:25]
    # )

    # def format_amount(x):
    #     x = round(abs(float(x)), 2)
    #     euros = int(x)
    #     cents = int(round((x - euros) * 100))
    #     return f"{euros:05d}_{cents:02d}"

    # trades["amount_id"] = trades["total"].apply(format_amount)

    # trades["id_base"] = (
    #     trades["date_id"] +
    #     trades["product_name_id"] +
    #     trades["amount_id"]
    # )

    # # --- Infinite duplicate handling ---
    # trades["dup_index"] = trades.groupby("id_base").cumcount()

    # trades["id"] = (
    #      trades["dup_index"].astype(str) + trades["id_base"]
    # )
    
    trades['broker']='fortuneo'
    # --- Final table ---
    return trades[[
        "date",
        "product_name",
        "description",
        "quantity",
        "price",
        'taxes',
        "amount",'total',
        # "id",
        'broker'
    ]].sort_values("date").reset_index(drop=True)
    
    import re

def extract_quantity(description: str) -> float:
    """
    Extrait la quantité depuis une description Degiro
    Ex: 'Kauf 32 @ 15,23' → 32
    Ex: 'Limit Kauf 10 @ ...' → 10
    """
    if not isinstance(description, str):
        return 0.0

    match = re.search(r"\b(\d+(?:\.\d+)?)\b", description)
    return float(match.group(1)) if match else 0.0



def compute_transactions_degiro(data_deg: pd.DataFrame) -> pd.DataFrame:
    data = data_deg.copy()

    # ------------------------------------------------------------------
    # 1) Identify transaction-related rows (faithful to original logic)
    # ------------------------------------------------------------------
    transac_idx = []

    for i in data.index:
        desc = str(data.loc[i, "description"])
        curr = str(data.loc[i, "currency"])
        prod = str(data.loc[i, "product_name"])

        if "gebühren" in desc:
            transac_idx.append(i)

        if "Währungswechsel (Ausbuchung)" in desc and prod != "nan" and "EUR" in curr:
            transac_idx.append(i)

        if "Währungswechsel (Einbuchung)" in desc and prod != "nan" and "EUR" in curr:
            transac_idx.append(i)

        if "Kauf" in desc and "EUR" in curr:
            transac_idx.append(i)

        if "Verkauf" in desc and "EUR" in curr:
            transac_idx.append(i)

        if "Kauf" in desc and "EUR" not in curr:
            data.loc[i, "amount"] = 0
            transac_idx.append(i)

        if "Verkauf" in desc and "EUR" not in curr:
            data.loc[i, "amount"] = 0
            transac_idx.append(i)

    tr_deg = data.loc[transac_idx].copy()

    # ------------------------------------------------------------------
    # 2) order_id cleanup / fallback
    # ------------------------------------------------------------------
    if len(tr_deg) > 0:
        if "order_id" in tr_deg.columns:
            tr_deg["order_id"] = tr_deg["order_id"].astype(str).str[:19]

        for i in tr_deg[
            tr_deg["order_id"].isna()
            & (~tr_deg["product_name"].str.contains("STANLEY|FUNDSHAR", na=False))
        ].index:
            tr_deg.loc[i, "order_id"] = randint(0, 10**25)

    # ------------------------------------------------------------------
    # 3) Rebuild aggregated transactions (as in original logic)
    # ------------------------------------------------------------------
    l_date, l_product_name, l_op = [], [], []
    l_quantity, l_price, l_currency = [], [], []
    l_taxes, l_amount = [], []

    special_words = ["DELISTING", "KAPITALERHÖHUNG", "AKTIENSPLIT", "SPIN-OFF"]

    for (order_id,) in tr_deg[["order_id"]].value_counts().index:
        block = tr_deg[tr_deg["order_id"] == order_id]

        l_product_name.append(block["product_name"].iloc[0])
        l_date.append(block["date"].iloc[0])

        amount_sum = block.loc[
            block["description"].str.contains("Ausbuchung|Einbuchung|Kauf|Verkauf", na=False),
            "amount"
        ].sum()

        tax_sum = block.loc[
            block["description"].str.contains("gebühren", na=False),
            "amount"
        ].sum()

        l_amount.append(amount_sum)
        l_taxes.append(tax_sum)

        qty = 0.0
        desc_trade = block.loc[
            block["description"].str.contains("Kauf|Verkauf", na=False),
            "description"
        ].values

        for d in desc_trade:
            # print(d)
            # if any(w in d for w in special_words):
            #     qty += float(d.split()[2])
            # else:
            #     qty += float(d.split()[1])
            qty += extract_quantity(d)

        if "Verkauf" in desc_trade[0]:
            l_op.append("Vente")
            l_quantity.append(-qty)
        else:
            l_op.append("Achat")
            l_quantity.append(qty)

        l_price.append(desc_trade[0].split()[4])
        l_currency.append(
            block.loc[
                block["description"].str.contains("Kauf|Verkauf", na=False),
                "currency"
            ].iloc[0]
        )

    table_deg = pd.DataFrame({
        "date": l_date,
        "product_name": l_product_name,
        "description": l_op,
        "price": l_price,
        "currency": l_currency,
        "quantity": l_quantity,
        "taxes": l_taxes,
        "amount": l_amount
    })

    table_deg["total"] = table_deg["amount"] + table_deg["taxes"]

    # ------------------------------------------------------------------
    # 4) ID generation (strict, fixed-width, duplicate-safe)
    # ------------------------------------------------------------------
    # table_deg["date_id"] = pd.to_datetime(table_deg["date"]).dt.strftime("%Y%m%d")

    # table_deg["product_name_id"] = (
    #     table_deg["product_name"]
    #         .fillna("")                # évite NaN
    # .astype(str)               # FORCE string
    # .str.upper()
    #     .str.replace(r"[^A-Z0-9]", "", regex=True)
    #     .str.ljust(25, "X")
    #     .str[:25]
    # )

    # def format_amount(x):
    #     x = round(abs(float(x)), 2)
    #     euros = int(x)
    #     cents = int(round((x - euros) * 100))
    #     return f"{euros:05d}_{cents:02d}"

    # table_deg["amount_id"] = table_deg["total"].apply(format_amount)

    # table_deg["id_base"] = (
    #     table_deg["date_id"] +
    #     table_deg["product_name_id"] +
    #     table_deg["amount_id"]
    # )

    # table_deg["dup_index"] = table_deg.groupby("id_base").cumcount()

    # table_deg["id"] = (
    #      table_deg["dup_index"].astype(str) + table_deg["id_base"]
    # )
    table_deg['broker'] ='degiro'
    # ------------------------------------------------------------------
    # 5) Final output
    # ------------------------------------------------------------------
    return table_deg.drop(columns=[
        # "date_id",
        # "product_name_id",
        # "amount_id",
        # "id_base",
        # "dup_index",
        'currency'
    ]).sort_values("date").reset_index(drop=True)


def apply_id(my_df:pd.DataFrame)->pd.DataFrame:
    my_df["date_id"] = pd.to_datetime(my_df["date"]).dt.strftime("%Y%m%d")

    my_df["product_name_id"] = (
        my_df["product_name"]
            .fillna("")                # évite NaN
    .astype(str)               # FORCE string
    .str.upper()
        .str.replace(r"[^A-Z0-9]", "", regex=True)
        .str.ljust(25, "X")
        .str[:25]
    )

    def format_amount(x):
        x = round(abs(float(x)), 2)
        euros = int(x)
        cents = int(round((x - euros) * 100))
        return f"{euros:05d}_{cents:02d}"

    my_df["amount_id"] = my_df["total"].apply(format_amount)

    my_df["id_base"] = (
        my_df["date_id"] +
        my_df["product_name_id"] +
        my_df["amount_id"]
    )

    my_df["dup_index"] = my_df.groupby("id_base").cumcount()

    my_df["id"] = (
        my_df["dup_index"].astype(str) + my_df["id_base"]
    )
    my_df.drop(columns=[
            "date_id", "product_name_id", "amount_id", "id_base", "dup_index",
        ],inplace=True)
    return my_df


def process_csv_incremental(
    csv_name: str,
    transactions: pd.DataFrame,
    base_path: str = "bank_statements/"
) -> tuple[pd.DataFrame, pd.DataFrame]:

    existing_ids = set(transactions['id'])
    dfs = []

    if 'FORTUNEO' in csv_name:
        df = pd.read_csv(
            base_path + csv_name + '.csv',
            encoding="ISO-8859-1",
            delimiter=";"
        )

        for res in [
            compute_dividends_fortuneo,
            compute_transactions_fortuneo
        ]:
            out = apply_id(
                merge_w_tickers(
                    res(normalize_fortuneo(df))
                )
            )
            if out is not None and not out.empty:
                dfs.append(out)

    elif 'DEGIRO' in csv_name:
        df = pd.read_csv(base_path + csv_name + '.csv')

        for res in [
            compute_dividends_degiro,
            compute_transactions_degiro
        ]:
            out = apply_id(
                merge_w_tickers(
                    res(normalize_degiro(df))
                )
            )
            if out is not None and not out.empty:
                dfs.append(out)

    if not dfs:
        return pd.DataFrame()

    new_df = pd.concat(dfs, ignore_index=True)
    new_df = new_df.loc[~new_df['id'].isin(existing_ids)]

    if new_df.empty:
        return pd.DataFrame()

    new_df = new_df.sort_values('date').reset_index(drop=True)

    transactions = pd.concat([transactions, new_df], ignore_index=True)

    return new_df

def log_added_rows(df: pd.DataFrame, csv_name: str, max_rows: int = 500):
    """
    Pretty-print details of newly added transactions.
    """
    if df.empty:
        print(f"{csv_name}: no new transactions")
        return

    print(f"\n{csv_name}: {len(df)} new transaction(s) added")

    cols = [c for c in ['date', 'product_name', 'description', 'total', 'id'] if c in df.columns]

    preview = df[cols].sort_values('date')

    if len(preview) > max_rows:
        print(preview.head(max_rows).to_string(index=False))
        print(f"... ({len(preview) - max_rows} more rows)")
    else:
        print(preview.to_string(index=False))
        
def convert_prices_to_eur(
    price_daily: pd.DataFrame,
    stock_cur: pd.DataFrame,
    drop_fx: bool = False
) -> pd.DataFrame:
    prices = price_daily.copy()
    # prices.columns = prices.columns.str.strip().str.upper()
    prices.index = pd.to_datetime(prices.index)

    stock_cur_norm = (
        stock_cur
        .assign(Tickers=lambda x: x['Tickers'].str.strip().str.upper())
    )

    currency_to_fx = {
        'USD': 'USDEUR=X',
        'GBP': 'GBPEUR=X',
        'GBp': 'GBpEUR=X',
        'SEK': 'SEKEUR=X',
        'PLN': 'PLNEUR=X',
    }

    prices_eur = prices.copy()

    for currency, fx_ticker in currency_to_fx.items():
        tickers = stock_cur_norm.loc[
            stock_cur_norm['Currency'] == currency, 'Tickers'
        ]
        tickers = [t for t in tickers if t in prices_eur.columns]

        if not tickers:
            continue

        if fx_ticker not in prices_eur.columns:
            raise ValueError(f"Missing FX series: {fx_ticker}")

        prices_eur[tickers] = prices_eur[tickers].mul(
            prices_eur[fx_ticker], axis=0
        )

    if drop_fx:
        prices_eur = prices_eur.drop(
            columns=list(currency_to_fx.values()),
            errors='ignore'
        )

    return prices_eur

def compute_portfolio_value_from_prices_positions(prices, positions):
    prices = prices.copy()
    positions = positions.copy()

    prices.index = pd.to_datetime(prices.index)
    positions.index = pd.to_datetime(positions.index)

    prices.columns = prices.columns.str.strip().str.upper()
    positions.columns = positions.columns.str.strip().str.upper()

    common = prices.columns.intersection(positions.columns)

    portfolio_by_stock = positions[common] * prices[common]
    portfolio_value = portfolio_by_stock.sum(axis=1, min_count=1)

    return portfolio_value, portfolio_by_stock

def append_df_to_csv(csv_path: str, df_new: pd.DataFrame) -> dict:
    """
    Safely append rows from a DataFrame to an existing CSV file.

    Returns:
        {
            "rows_added": int,
            "file_size_bytes": int,
            "status": "ok" | "error",
            "message": str
        }
    """

    result = {
        "rows_added": 0,
        "file_size_bytes": 0,
        "status": "error",
        "message": ""
    }
    st.write(df_new)
    try:
        # ---------- Basic checks ----------
        if not os.path.exists(csv_path):
            result["message"] = f"File does not exist: {csv_path}"
            return result

        if df_new.empty:
            result["status"] = "ok"
            result["message"] = "No rows to add (DataFrame is empty)."
            result["file_size_bytes"] = os.path.getsize(csv_path)
            return result

        # ---------- Read header of existing CSV ----------
        df_existing_head = pd.read_csv(csv_path, nrows=0)
        existing_cols = list(df_existing_head.columns)
        new_cols = list(df_new.columns)

        if set(existing_cols) != set(new_cols):
            result["message"] = (
                "Column mismatch.\n"
                f"CSV columns: {existing_cols}\n"
                f"New DF columns: {new_cols}"
            )
            st.write(df_new)
            return result

        # ---------- Write safely via temp file ----------
        df_new=df_new[existing_cols]
        with NamedTemporaryFile(mode="w", delete=False, newline="", suffix=".csv") as tmp_file:
            temp_path = tmp_file.name

        # Copy original file content first
        shutil.copyfile(csv_path, temp_path)

        # Append new rows to temp file
        df_new.to_csv(temp_path, mode="a", header=False, index=False)

        # Atomic replace (safe swap)
        os.replace(temp_path, csv_path)

        # ---------- Success ----------
        rows_added = len(df_new)
        file_size = os.path.getsize(csv_path)

        result.update({
            "rows_added": rows_added,
            "file_size_bytes": file_size,
            "status": "ok",
            "message": "Rows appended successfully."
        })

        return result

    except Exception as e:
        result["message"] = str(e)
        return result
    
def transac_to_portfolio(my_path:str)->pd.DataFrame:    
    # -----------------------------
    # 1. Prepare data
    # -----------------------------
    df = pd.read_csv(my_path)
    df["date"] = pd.to_datetime(df["date"])
    # Keep only buy / sell operations
    trades = df[df["description"].isin(["Achat", "Vente"])]
    trades=df.copy()
    # Quantity is already signed:
    # Achat  -> positive
    # Vente  -> negative
    trades["quantity"] = trades["quantity"].astype(float)
    # -----------------------------
    # 2. Net quantity per day per stock
    # -----------------------------
    daily_trades = (
        trades
        .groupby(["date", "tickers"], as_index=False)["quantity"]
        .sum()
    )
    # -----------------------------
    # 3. Build full daily date index
    # -----------------------------
    full_dates = pd.date_range(
        start=daily_trades["date"].min(),
        end=pd.Timestamp.today().normalize(),
        freq="D"
    )
    # -----------------------------
    # 4. Daily positions per stock
    # -----------------------------
    portfolio = (
        daily_trades
        .set_index(["date", "tickers"])
        .unstack(fill_value=0)      # rows = dates, columns = tickers
        .reindex(full_dates, fill_value=0)
        .cumsum()
    )
    # Optional: nicer column names
    portfolio.columns = portfolio.columns.droplevel(0)
    portfolio.index.name = "date"

    # -----------------------------
    # 5. Results
    # -----------------------------

    # A) Shares held per stock per day
    # B) Total portfolio quantity per day
    
    portfolio[portfolio < 0] = 0
    return portfolio


def transac_to_df(my_path:str)->dict:
    '''
    return dict with following keys ['Dividende','Barausgleich','Kapitalrückzahlung','Achat','Vente']
    
    '''    
    # -----------------------------
    # 1. Prepare data
    # -----------------------------
    df = pd.read_csv(my_path)
    df["date"] = pd.to_datetime(df["date"])
    # Keep only buy / sell operations
    my_income_stocks = {}
    my_inc_stock ={}
    for i in ['Dividende','Barausgleich','Kapitalrückzahlung','Achat','Vente']:
        my_income_stocks[i] = df[df["description"].isin([i])].copy()
        # Quantity is already signed:
        # Achat  -> positive
        # Vente  -> negative
        my_income_stocks[i]["total"] = my_income_stocks[i]["total"].astype(float)
        # -----------------------------
        # 2. Net quantity per day per stock
        # -----------------------------
        daily_trades = (
            my_income_stocks[i]
            .groupby(["date", "tickers"], as_index=False)["total"]
            .sum()
        )
        # -----------------------------
        # 3. Build full daily date index
        # -----------------------------
        full_dates = pd.date_range(
            start=daily_trades["date"].min(),
            end=pd.Timestamp.today().normalize(),
            freq="D"
        )
        # -----------------------------
        # 4. Daily positions per stock
        # -----------------------------
        positions = (
            daily_trades
            .set_index(["date", "tickers"])
            .unstack(fill_value=0)      # rows = dates, columns = tickers
            .reindex(full_dates, fill_value=0)
            .cumsum()
        )
        # Optional: nicer column names
        positions.columns = positions.columns.droplevel(0)
        positions.index.name = "date"

        # -----------------------------
        # 5. Results
        # -----------------------------

        # A) Shares held per stock per day
        # B) Total portfolio quantity per day
        if i!='Achat':
            positions[positions < 0] = 0
        my_inc_stock[i] = positions
    return my_inc_stock



def date_stock()->pd.DataFrame:
    import datetime
    stock_data = pd.read_csv('master_data/stock_final2')
    # stock_data.sort_values(by='Date')
    stock_cur =stock_data[['Tickers','Currency']].drop_duplicates().reset_index(drop=True)

    prices = (
        stock_data
        .rename(columns={'Date': 'date','Tickers':'tickers'})
        .pivot_table(
            index='date',
            columns=('tickers'),
            values='Close',
            aggfunc='last'   # <-- KEY FIX
        )
        .sort_index()
    )
    prices.index = pd.to_datetime(prices.index)
    full_index = pd.date_range(
        start=prices.index.min(),
        # end=prices.index.max(),
        end = pd.to_datetime(datetime.datetime.today()),
        freq='D'
    )
    prices_daily = prices.reindex(full_index).ffill()
    prices_daily = prices_daily.bfill()
    return prices_daily,stock_cur,full_index

# -----------------------------
# 1. Prepare data
# -----------------------------
def sav_int_prop(my_path)->dict:
    savings = pd.read_csv(my_path)
    df = savings.copy()
    df["date"] = pd.to_datetime(df["Date"])
    # Keep only buy / sell operations
    my_temp_saving = {}
    my_saving ={}
    for i in ['Saving', 'Interest', 'Property']:
        my_temp_saving[i] = df[df["Description"].isin([i])].copy()
        # Quantity is already signed:
        # Achat  -> positive
        # Vente  -> negative
        my_temp_saving[i]["Total"] = my_temp_saving[i]["Total"].astype(float)
        # -----------------------------
        # 2. Net quantity per day per stock
        # -----------------------------
        daily_trades = (
            my_temp_saving[i]
            .groupby(["date", "Product"], as_index=False)["Total"]
            .sum()
        )
        # -----------------------------
        # 3. Build full daily date index
        # -----------------------------
        full_dates = pd.date_range(
            start=daily_trades["date"].min(),
            end=pd.Timestamp.today().normalize(),
            freq="D"
        )
        # -----------------------------
        # 4. Daily positions per stock
        # -----------------------------
        positions = (
            daily_trades
            .set_index(["date", "Product"])
            .unstack(fill_value=0)      # rows = dates, columns = tickers
            .reindex(full_dates, fill_value=0)
            .cumsum()
        )
        # Optional: nicer column names
        positions.columns = positions.columns.droplevel(0)
        positions.index.name = "date"

        # -----------------------------
        # 5. Results
        # -----------------------------

        # A) Shares held per stock per day
        # B) Total portfolio quantity per day
        positions[positions<0.001]=0
        my_saving[i] = positions
    return my_saving

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
    start = datetime(2020, 10, 1)

    remb = dict({
        datetime(2020, 11, 1): 9250,
        datetime(2021, 6, 1): 9250,
        datetime(2022, 9, 1): 9250,
        datetime(2023, 2, 1): 9250,
        datetime(2025, 7, 1): 7150,

    })

    date = [start]
    total_debt = [amount-430.12]
    interest = [151.24]
    principal = [430.12]
    monthly_payment = [rate]

    for i in range(1, 360, 1):
        # if((start+relativedelta(months=i))<=datetime.today()):
        if ((total_debt[-1] > 0)):

            date.append(start+relativedelta(months=i))
            interest.append(round(total_debt[-1]*inter/1200,2))
            # total_debt.append(round(total_debt[-1]-principal[-1],2))
            # interest.append(round(total_debt[-1]*inter/1200,2))
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
            total_debt.append(round(total_debt[-1]-principal[-1],2))
    tableau["date"] = date
    tableau["total_debt"] = total_debt
    tableau["interest"] = interest
    tableau["principal"] = principal
    tableau["monthly_payment"] = monthly_payment
    tableau["property_value"] = 325000

    return tableau

def my_debt():
    my_credit = credit()[['date','total_debt']]
    full_dates = pd.date_range(
        start=my_credit["date"].min(),
        end=pd.Timestamp.today().normalize(),
        freq="D"
    )
    # -----------------------------
    # 4. Daily positions per stock
    # -----------------------------
    positions = (
        my_credit
        .set_index(["date"])
        # .unstack(fill_value=0)      # rows = dates, columns = tickers
        .reindex(full_dates)
        .ffill()
    )
    # Optional: nicer column names
    # positions.columns = positions.columns.droplevel(0)
    positions.index.name = "date"
    my_debt=positions.copy()
    return my_debt


def build_car_value_series(
    date_index,
    car_name: str,
    buy_value: float,
    buy_date,
    depreciation_rate: float,
    sell_date=None,
    sell_value=None,
):
    """
    Create a daily car value series.

    Parameters
    ----------
    date_index : pd.DatetimeIndex
        Index of your patrimoine dataframe (daily dates)
    car_name : str
        Name of the car (used as column name)
    buy_value : float
        Purchase price of the car
    buy_date : str or datetime
        Date the car was bought
    depreciation_rate : float
        Annual depreciation rate (e.g. 0.15 for -15% per year)
    sell_date : str or datetime, optional
        Date the car was sold
    sell_value : float, optional
        Resale price (if provided, linear interpolation to that value)

    Returns
    -------
    pd.DataFrame with one column = car_name
    """

    buy_date = pd.to_datetime(buy_date)
    sell_date = pd.to_datetime(sell_date) if sell_date else None

    values = pd.Series(0.0, index=date_index)

    # Only start valuing after purchase
    active_mask = date_index >= buy_date
    active_dates = date_index[active_mask]

    if sell_date and sell_value is not None:
        # Linear depreciation between buy and sell
        total_days = (sell_date - buy_date).days
        days_held = (active_dates - buy_date).days.clip(lower=0)

        linear_values = buy_value + (sell_value - buy_value) * (days_held / total_days)
        linear_values[active_dates > sell_date] = 0  # car gone after sale

        values.loc[active_dates] = linear_values

    else:
        # Exponential depreciation (declining balance)
        days_held = (active_dates - buy_date).days
        years_held = days_held / 365.25

        depreciated_values = buy_value * ((1 - depreciation_rate) ** years_held)
        values.loc[active_dates] = depreciated_values

    return pd.DataFrame({car_name: values})

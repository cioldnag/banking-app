

import yfinance as yf
import pandas as pd
# from datetime import datetime
import datetime
from concurrent.futures import ThreadPoolExecutor
import time

start_time = time.time()

# --- 1. Load files efficiently
stock_histo = pd.read_csv("/Users/loicg/OneDrive/Documents/IT/banking_optimized/master_data/stock_final2", usecols=["Date", "Close", "Tickers", "Currency"])
tickers_list = pd.read_csv("/Users/loicg/OneDrive/Documents/IT/banking_optimized/master_data/product_tickers_currency_plus.csv", sep=",")["tickers"].unique()
tickers_list = [x for x in tickers_list if isinstance(x,str)]
print('-'.join([x for x in tickers_list if isinstance(x,str)]))
# --- 2. Compute start/end dates
date_histo = stock_histo["Date"].iloc[-15]
print(date_histo)
start = pd.to_datetime(date_histo)
end = datetime.datetime.today()

# --- 3. Clean tickers
excluded = ['DPW.DE', 'NGPN.L', 'GEHCV', 'EDF.PA', 'URW.AS', 'SOLV-WI','KLG-WI','IQQR.DE', 'IML.PA','DELL','KN.PA']
tickers = [x for x in tickers_list if x not in excluded]

# --- 4. Helper function to download a chunk of tickers
def download_chunk(subset):
    data = yf.download(subset, start=start, end=end, progress=False, group_by='ticker', threads=False)
    frames = []
    if isinstance(data.columns, pd.MultiIndex):
        for ticker in data.columns.levels[0]:
            try:
                df = data.xs(ticker, axis=1, level=0, drop_level=True)
                df = df.reset_index()
                df["Tickers"] = ticker
                frames.append(df[["Date", "Close", "Tickers"]])
            except Exception:
                continue
    else:
        df = data.reset_index()
        df["Tickers"] = subset[0] if isinstance(subset, list) else subset
        frames.append(df[["Date", "Close", "Tickers"]])
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()

# --- 5. Split tickers into 3 roughly equal chunks
chunks = [tickers[i::6] for i in range(6)]
print(chunks)
# --- 6. Run 3 threads in parallel
with ThreadPoolExecutor(max_workers=6) as executor:
    results = list(executor.map(download_chunk, chunks))
    print(results)
# --- 7. Combine results
stock_final = pd.concat(results, ignore_index=True)
st.write(stock_final[stock_final['Tickers']=='AAPL'])
print(stock_final[stock_final['Tickers']=='SAN.PA'])
print(stock_final[stock_final['Tickers']=='USDEUR=X '])
stock_final["Date"] = pd.to_datetime(stock_final["Date"])

# --- 8. Merge and finalize
ti_cu = pd.read_csv("/Users/loicg/OneDrive/Documents/IT/banking_optimized/master_data/product_tickers_currency_plus.csv", sep=",")[["tickers", "currency"]]
stock_final = pd.merge(stock_final, ti_cu, left_on="Tickers", how="left",right_on='tickers')
stock_final.drop(columns=['tickers'],inplace=True)
stock_final.rename(columns={'currency':'Currency'},inplace=True)
stock_histo = pd.concat([ stock_histo,stock_final], ignore_index=True)
stock_histo["Date"] = (
    pd.to_datetime(stock_histo["Date"], format='mixed', errors='coerce')
    .dt.strftime("%Y-%m-%d")
)
st.write(stock_histo[stock_histo['Tickers']=='AAPL'])
stock_histo.drop_duplicates(subset=["Date", "Tickers"], keep="last", inplace=True)
stock_histo.sort_values(["Tickers", "Date"], inplace=True)
st.write(stock_histo[stock_histo['Tickers']=='AAPL'])

# --- 9. Save
stock_histo["Date"] = (
    pd.to_datetime(stock_histo["Date"], format='mixed', errors='coerce')
    .dt.strftime("%Y-%m-%d")
)
stock_histo.to_csv("/Users/loicg/OneDrive/Documents/IT/banking_optimized/master_data/stock_final2", index=False)

print(f"--- {time.time() - start_time:.2f} seconds ---")

# function version
def update_stock_values():

    import yfinance as yf
    from concurrent.futures import ThreadPoolExecutor
    import time
    start_time = time.time()

    # --- 1. Load files efficiently
    stock_histo = pd.read_csv("master_data/stock_final2", usecols=["Date", "Close", "Tickers", "Currency"])
    tickers_list = pd.read_csv("master_data/product_tickers_currency_plus.csv", sep=",")["tickers"].unique()
    tickers_list = [x for x in tickers_list if isinstance(x,str)]
    print('-'.join([x for x in tickers_list if isinstance(x,str)]))
    # --- 2. Compute start/end dates
    date_histo = stock_histo["Date"].iloc[-15]
    print(date_histo)
    start = pd.to_datetime(date_histo)
    end = datetime.datetime.today()

    # --- 3. Clean tickers
    excluded = ['DPW.DE', 'NGPN.L', 'GEHCV', 'EDF.PA', 'URW.AS', 'SOLV-WI','KLG-WI','IQQR.DE', 'IML.PA','DELL','KN.PA']
    tickers = [x for x in tickers_list if x not in excluded]

    # --- 4. Helper function to download a chunk of tickers
    def download_chunk(subset):
        data = yf.download(subset, start=start, end=end, progress=False, group_by='ticker', threads=False)
        frames = []
        if isinstance(data.columns, pd.MultiIndex):
            for ticker in data.columns.levels[0]:
                try:
                    df = data.xs(ticker, axis=1, level=0, drop_level=True)
                    df = df.reset_index()
                    df["Tickers"] = ticker
                    frames.append(df[["Date", "Close", "Tickers"]])
                except Exception:
                    continue
        else:
            df = data.reset_index()
            df["Tickers"] = subset[0] if isinstance(subset, list) else subset
            frames.append(df[["Date", "Close", "Tickers"]])
        return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()

    # --- 5. Split tickers into 3 roughly equal chunks
    chunks = [tickers[i::6] for i in range(6)]
    print(chunks)
    # --- 6. Run 3 threads in parallel
    with ThreadPoolExecutor(max_workers=6) as executor:
        results = list(executor.map(download_chunk, chunks))
        print(results)
    # --- 7. Combine results
    stock_final = pd.concat(results, ignore_index=True)
    print(stock_final[stock_final['Tickers']=='SAN.PA'])
    print(stock_final[stock_final['Tickers']=='USDEUR=X '])
    stock_final["Date"] = pd.to_datetime(stock_final["Date"])

    # --- 8. Merge and finalize
    ti_cu = pd.read_csv("master_data/product_tickers_currency_plus.csv", sep=",")[["tickers", "currency"]]
    stock_final = pd.merge(stock_final, ti_cu, left_on="Tickers", how="left",right_on='tickers')
    stock_final.drop(columns=['tickers'],inplace=True)
    stock_final.rename(columns={'currency':'Currency'},inplace=True)
    stock_histo = pd.concat([stock_histo, stock_final], ignore_index=True)
    stock_histo.drop_duplicates(subset=["Date", "Tickers"], keep="last", inplace=True)
    stock_histo.sort_values(["Tickers", "Date"], inplace=True)

    # --- 9. Save
    stock_histo["Date"] = (
        pd.to_datetime(stock_histo["Date"], format='mixed', errors='coerce')
        .dt.strftime("%Y-%m-%d")
    )
    stock_histo.to_csv("master_data/stock_final2", index=False)

    print(f"--- {time.time() - start_time:.2f} seconds ---")
    return "function finished"
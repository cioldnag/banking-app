# import yfinance as yf
# import pandas as pd
# import datetime

# from datetime import datetime
# from datetime import timedelta, date
# import time 
# start_time = time.time()

# stock_histo = pd.read_csv("stock_final2")
# tickers_list = pd.read_csv(
#     "data/product_tickers_currency.csv", sep=";").Tickers.unique()
# date_histo = stock_histo.Date.values[-7]
# end = datetime.today()
# start = datetime(int(date_histo[0:4]), int(
#     date_histo[5:7]), int(date_histo[8:]))

# stock_final = pd.DataFrame()
# # iterate over each symbol
# for i in tickers_list:
#     try:
#         # download the stock price
#         stock = []
#         stock = yf.download(i, progress=False, start=start, end=end)

#         # append the individual stock prices
#         if len(stock) == 0:
#             continue
#         else:
#             stock['Name'] = i
#             stock_final = pd.concat([stock, stock_final])
#     except Exception:
#         continue
# # stock_final.reset_index(level=[0], inplace=True)
# # stock_final.rename(columns={'Name': "Tickers"}, inplace=True)

# stock_final = stock_final.stack(level=1).reset_index().dropna(subset=['Close'])
# stock_final.rename(columns={'Ticker': 'Tickers'}, inplace=True)

# stock_final["Date"] = pd.to_datetime(stock_final["Date"])
# stock_final2 = stock_final.copy(deep=True)
# ti_cu = pd.read_csv("data/product_tickers_currency.csv", sep=";")
# ti_cu = ti_cu[["Tickers",	"Currency"]]
# stock_final = pd.merge(stock_final, ti_cu, on="Tickers")
# stock_final = stock_final[["Date", "Close", "Tickers", "Currency"]]
# stock_histo = pd.concat([stock_histo, stock_final])
# stock_histo["Date"] = pd.to_datetime(stock_histo["Date"])
# stock_histo.sort_values(by=["Tickers", "Date"], inplace=True)
# stock_histo.drop_duplicates(
#     subset=["Date", "Tickers"], inplace=True, keep="last")
# stock_histo.reset_index(inplace=True)
# stock_histo.drop(columns=["index", "Unnamed: 0"], inplace=True)
# stock_histo = stock_histo[["Date", "Close", "Tickers", "Currency"]]
# stock_histo.to_csv("stock_final2")
# print("--- %s seconds ---" % (time.time() - start_time))


# import yfinance as yf
# import pandas as pd
# from datetime import datetime
# import time

# start_time = time.time()

# # --- 1. Load files efficiently
# stock_histo = pd.read_csv("stock_final2", usecols=["Date", "Close", "Tickers", "Currency"])
# tickers_list = pd.read_csv("data/product_tickers_currency.csv", sep=";")["Tickers"].unique()

# # --- 2. Compute start/end dates
# date_histo = stock_histo["Date"].iloc[-7]
# start = pd.to_datetime(date_histo)
# end = datetime.today()

# # --- 3. Download all tickers (multi-threaded)
# data = yf.download(
#     tickers_list.tolist(),
#     start=start,
#     end=end,
#     progress=False,
#     group_by='ticker',
#     threads=True
# )

# # --- 4. Normalize structure depending on output type
# frames = []

# if isinstance(data.columns, pd.MultiIndex):
#     # Multiple tickers: multi-level columns
#     for ticker in data.columns.levels[1]:
#         try:
#             df = data.xs(ticker, axis=1, level=1, drop_level=False)
#             df = df.reset_index()
#             df["Tickers"] = ticker
#             frames.append(df[["Date", ("Close", ticker)]].rename(columns={("Close", ticker): "Close"}))
#         except Exception:
#             continue
# else:
#     # Single ticker
#     df = data.reset_index()
#     df["Tickers"] = tickers_list[0]
#     frames.append(df[["Date", "Close", "Tickers"]])

# # --- 5. Merge and finalize
# if frames:
#     stock_final = pd.concat(frames, ignore_index=True)
#     ti_cu = pd.read_csv("data/product_tickers_currency.csv", sep=";")[["Tickers", "Currency"]]
#     stock_final = pd.merge(stock_final, ti_cu, on="Tickers", how="left")

#     stock_histo = pd.concat([stock_histo, stock_final], ignore_index=True)
#     stock_histo.drop_duplicates(subset=["Date", "Tickers"], keep="last", inplace=True)
#     stock_histo.sort_values(["Tickers", "Date"], inplace=True)

#     stock_histo.to_csv("stock_final3", index=False)
#     print('line_114')
# print(f"--- {time.time() - start_time:.2f} seconds ---")

import yfinance as yf
import pandas as pd
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import time

start_time = time.time()

# --- 1. Load files efficiently
stock_histo = pd.read_csv("/Users/loicg/OneDrive/Documents/IT/banking/stock_final2", usecols=["Date", "Close", "Tickers", "Currency"])
tickers_list = pd.read_csv("/Users/loicg/OneDrive/Documents/IT/banking/data/product_tickers_currency.csv", sep=";")["Tickers"].unique()
print('-'.join(tickers_list))
# --- 2. Compute start/end dates
date_histo = stock_histo["Date"].iloc[-15]
print(date_histo)
start = pd.to_datetime(date_histo)
end = datetime.today()

# --- 3. Clean tickers
excluded = ['DPW.DE', 'NGPN.L', 'GEHCV', 'EDF.PA', 'URW.AS', 'SOLV-WI','KLG-WI','IQQR.DE', 'IML.PA','DELL']
tickers = [x for x in tickers_list.tolist() if x not in excluded]

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
ti_cu = pd.read_csv("/Users/loicg/OneDrive/Documents/IT/banking/data/product_tickers_currency.csv", sep=";")[["Tickers", "Currency"]]
stock_final = pd.merge(stock_final, ti_cu, on="Tickers", how="left")

stock_histo = pd.concat([stock_histo, stock_final], ignore_index=True)
stock_histo.drop_duplicates(subset=["Date", "Tickers"], keep="last", inplace=True)
stock_histo.sort_values(["Tickers", "Date"], inplace=True)

# --- 9. Save
stock_histo["Date"] = (
    pd.to_datetime(stock_histo["Date"], format='mixed', errors='coerce')
    .dt.strftime("%Y-%m-%d")
)
stock_histo.to_csv("/Users/loicg/OneDrive/Documents/IT/banking/stock_final2", index=False)

print(f"--- {time.time() - start_time:.2f} seconds ---")
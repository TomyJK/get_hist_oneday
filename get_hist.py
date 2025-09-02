import pandas as pd
from kiteconnect import KiteConnect
import datetime as dt
import os
from get_token_latest import get_access_token

# === Kite setup ===
your_access_token = get_access_token()
kite = KiteConnect(api_key="hwdft0qevt0p4vxb")
kite.set_access_token(your_access_token)

# === Paths ===
downloads = r"C:\Users\HP\Desktop\Downloads"
input_file = os.path.join(downloads, "stocksDd.xlsx")
output_file = os.path.join(downloads, "onedayhist_OHLCV.xlsx")

# === Load stock list ===
# Assuming columns: Symbol | Token
df_stocks = pd.read_excel(input_file)

# === Date for historical data ===
date = dt.date(2015, 4, 1)   # change date here
start = dt.datetime.combine(date, dt.time(9, 15))
end = dt.datetime.combine(date, dt.time(15, 30))

# === Fetch OHLCV ===
data_list = []

for _, row in df_stocks.iterrows():
    try:
        token = int(row["token"])
        ohlc = kite.historical_data(token, start, end, interval="day")
        if ohlc:
            d = ohlc[0]  # only one candle for "day"
            d["symbol"] = row["symbol"]
            data_list.append(d)
    except Exception as e:
        print(f"Error fetching {row['symbol']}: {e}")

# === Save to Excel ===
df_out = pd.DataFrame(data_list)
df_out = df_out[["symbol", "date", "open", "high", "low", "close", "volume"]]
df_out["date"] = pd.to_datetime(df_out["date"]).dt.tz_localize(None)
df_out["diff%"] = ((df_out["close"] - df_out["open"]) / df_out["open"]) * 100
df_out["diff%"] = df_out["diff%"].round(2)

df_out.to_excel(output_file, index=False)
print(f"Saved OHLCV to {output_file}")

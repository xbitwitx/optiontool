import yfinance as yf
import pandas as pd
from datetime import datetime
import argparse

def get_current_price(stock):
    try:
        return stock.info.get('regularMarketPrice') or stock.history(period="1d")["Close"].iloc[-1]
    except Exception as e:
        print(f"Error getting price: {e}")
        return None

def find_spreads(symbol, max_days=30, min_prob=0.70):
    stock = yf.Ticker(symbol)
    price = get_current_price(stock)
    if price is None:
        return pd.DataFrame()  # Return empty DataFrame if we can't get the price

    today = datetime.now().date()
    
    spreads = []
    for exp in stock.options:
        days = (datetime.strptime(exp, "%Y-%m-%d").date() - today).days
        if days > max_days:
            continue
        
        try:
            puts = stock.option_chain(exp).puts.sort_values('strike')
        except Exception as e:
            print(f"Error fetching option chain for {exp}: {e}")
            continue

        for i in range(len(puts) - 1):
            short, long = puts.iloc[i], puts.iloc[i + 1]
            credit = short['lastPrice'] - long['lastPrice']
            width = long['strike'] - short['strike']
            breakeven = short['strike'] - credit
            
            iv = (short['impliedVolatility'] + long['impliedVolatility']) / 2
            std_dev = price * iv * (days / 365)**0.5
            prob = 1 - (breakeven - price) / std_dev
            
            if prob >= min_prob:
                spreads.append({
                    'exp': exp,
                    'short': short['strike'],
                    'long': long['strike'],
                    'credit': credit,
                    'max_loss': width - credit,
                    'breakeven': breakeven,
                    'prob': prob,
                    'days': days
                })
    
    return pd.DataFrame(spreads)

def main():
    parser = argparse.ArgumentParser(description="Find profitable put spreads")
    parser.add_argument("symbol", help="Stock symbol (e.g., AAPL)")
    parser.add_argument("--output", default="spreads.csv", help="Output file name")
    args = parser.parse_args()

    try:
        spreads = find_spreads(args.symbol)
        if not spreads.empty:
            print(f"Potential spreads for {args.symbol}:")
            print(spreads.sort_values('prob', ascending=False).to_string(index=False))
            spreads.to_csv(args.output, index=False)
            print(f"\nResults saved to {args.output}")
        else:
            print(f"No suitable spreads found for {args.symbol}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()


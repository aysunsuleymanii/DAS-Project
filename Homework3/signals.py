import pandas as pd

def load_data():
    # Load the CSV file containing the stock data
    return pd.read_csv('data.csv')

def generate_signals(df):
    # Initialize a column for the signals
    df['Signal'] = 'Hold'  # Default signal is 'Hold'

    # RSI Buy/Sell signals
    df.loc[df['RSI_1D'] < 30, 'Signal'] = 'Buy'  # RSI below 30 (oversold)
    df.loc[df['RSI_1D'] > 70, 'Signal'] = 'Sell'  # RSI above 70 (overbought)

    # MACD Buy/Sell signals
    df.loc[(df['MACD_1D'] > df['MACD_signal_1D']) & (
                df['MACD_1D'].shift(1) <= df['MACD_signal_1D'].shift(1)), 'Signal'] = 'Buy'  # Bullish crossover
    df.loc[(df['MACD_1D'] < df['MACD_signal_1D']) & (
                df['MACD_1D'].shift(1) >= df['MACD_signal_1D'].shift(1)), 'Signal'] = 'Sell'  # Bearish crossover

    # Stochastic Oscillator Buy/Sell signals
    df.loc[df['Stochastic_1D'] < 20, 'Signal'] = 'Buy'  # Below 20 (oversold)
    df.loc[df['Stochastic_1D'] > 80, 'Signal'] = 'Sell'  # Above 80 (overbought)

    # EMA Buy/Sell signals
    df.loc[df['last_trade_price'] > df['EMA_fast_1W'], 'Signal'] = 'Buy'  # Price above EMA Fast
    df.loc[df['last_trade_price'] < df['EMA_slow_1W'], 'Signal'] = 'Sell'  # Price below EMA Slow

    # SMA Buy/Sell signals
    df.loc[df['last_trade_price'] > df['SMA_1D'], 'Signal'] = 'Buy'  # Price above SMA
    df.loc[df['last_trade_price'] < df['SMA_1D'], 'Signal'] = 'Sell'  # Price below SMA

    # Bollinger Bands Buy/Sell signals
    df.loc[df['last_trade_price'] < df['BB_Lower_1D'], 'Signal'] = 'Buy'  # Price below lower band
    df.loc[df['last_trade_price'] > df['BB_Upper_1D'], 'Signal'] = 'Sell'  # Price above upper band

    # Get the latest signal (last row)
    latest_signal = df['Signal'].iloc[-1]  # Signal for the latest date

    return latest_signal

# Example usage
if __name__ == "__main__":
    df = load_data()
    latest_signal = generate_signals(df)
    print(latest_signal)

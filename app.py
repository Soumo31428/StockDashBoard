from taipy.gui import Gui, State, navigate
import pandas as pd
from utils import get_stock_data, calculate_metrics, create_price_chart, format_number, get_stock_news
from datetime import datetime

# Default Indian and US stocks
default_stocks = [
    'RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS', 'INFY.NS', 'ICICIBANK.NS',  # Indian stocks
    'AAPL', 'GOOGL', 'MSFT', 'AMZN', 'META'  # US stocks
]

# Page layouts
root_md = """
<|layout|columns=1 1|
<|part|class_name=sidebar|
# Stock Analysis Dashboard

<|{selected_stock}|selector|lov={default_stocks}|label=Select Stock|>

<|{time_period}|selector|lov={['1mo', '3mo', '6mo', '1y', '2y', '5y']}|label=Time Period|>

<|Submit|button|on_action=submit_analysis|>
|>

<|part|class_name=main-content|
<|content|>
|>
|>
"""

analysis_md = """
# 📈 Stock Analysis: {selected_stock}

<|layout|columns=1 1 1 1|class_name=metrics-grid|
<|part|class_name=metric-card|
### Current Price
<|{current_price}|text|class_name=metric-value|>
|>

<|part|class_name=metric-card|
### 24h Change
<|{price_change}|text|class_name=metric-value {change_class}|>
|>

<|part|class_name=metric-card|
### Market Cap
<|{market_cap}|text|class_name=metric-value|>
|>

<|part|class_name=metric-card|
### Volume
<|{volume}|text|class_name=metric-value|>
|>
|>

<|{chart}|chart|>

<|layout|columns=1 1|
<|part|
### Key Statistics
<|{metrics_df}|table|>
|>

<|part|
### Latest News
<|{news_items}|table|show_all|>
|>
|>
"""

# Initial state
initial_state = {
    "selected_stock": "RELIANCE.NS",
    "time_period": "1y",
    "current_price": "",
    "price_change": "",
    "change_class": "",
    "market_cap": "",
    "volume": "",
    "chart": None,
    "metrics_df": pd.DataFrame(),
    "news_items": pd.DataFrame()
}

def submit_analysis(state: State):
    """Handle submit button click"""
    hist_data, stock_info = get_stock_data(state.selected_stock, state.time_period)
    
    if hist_data is not None and stock_info is not None:
        # Calculate metrics
        df = calculate_metrics(hist_data)
        
        # Update state with new data
        state.current_price = f"${format_number(stock_info.get('currentPrice', 0))}"
        change = stock_info.get('regularMarketChangePercent', 0)
        state.price_change = f"{change:.2f}%"
        state.change_class = "positive" if change >= 0 else "negative"
        state.market_cap = f"${format_number(stock_info.get('marketCap', 0))}"
        state.volume = format_number(stock_info.get('volume', 0))
        
        # Create chart
        state.chart = create_price_chart(df, state.selected_stock)
        
        # Create metrics dataframe
        state.metrics_df = pd.DataFrame({
            'Metric': ['P/E Ratio', 'EPS', '52 Week High', '52 Week Low', 'Beta'],
            'Value': [
                format_number(stock_info.get('trailingPE', 0)),
                format_number(stock_info.get('trailingEps', 0)),
                format_number(stock_info.get('fiftyTwoWeekHigh', 0)),
                format_number(stock_info.get('fiftyTwoWeekLow', 0)),
                format_number(stock_info.get('beta', 0))
            ]
        })
        
        # Get news
        state.news_items = get_stock_news(state.selected_stock)
        
        # Navigate to analysis page
        navigate(state, "analysis")

# Create Taipy GUI instance
pages = {
    "/": root_md,
    "analysis": analysis_md
}

css = """
.sidebar {
    background-color: #2D2D2D;
    padding: 20px;
    border-radius: 8px;
}

.main-content {
    padding: 20px;
}

.metrics-grid {
    gap: 16px;
}

.metric-card {
    background-color: #2D2D2D;
    padding: 16px;
    border-radius: 8px;
    transition: transform 300ms ease;
}

.metric-card:hover {
    transform: translateY(-2px);
}

.metric-value {
    font-family: 'Roboto Mono', monospace;
    font-size: 1.2rem;
}

.positive {
    color: #4BFF4B;
}

.negative {
    color: #FF4B4B;
}
"""

gui = Gui(pages=pages, css=css)
gui.run(port=5000, host="0.0.0.0", dark_mode=True, use_reloader=True)

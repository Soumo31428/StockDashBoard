import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import trafilatura
from datetime import datetime, timedelta

def get_stock_data(symbol, period='1y', start_date=None, end_date=None):
    """Fetch stock data using yfinance"""
    try:
        stock = yf.Ticker(symbol)
        if period == 'custom' and start_date and end_date:
            hist = stock.history(start=start_date, end=end_date)
        else:
            hist = stock.history(period=period)
        info = stock.info
        return hist, info
    except Exception as e:
        print(f"Error fetching stock data: {str(e)}")
        return None, None

def calculate_metrics(df):
    """Calculate technical indicators"""
    # Basic moving averages
    df['SMA_20'] = df['Close'].rolling(window=20).mean()
    df['SMA_50'] = df['Close'].rolling(window=50).mean()

    # RSI
    df['RSI'] = calculate_rsi(df['Close'])

    # MACD
    exp1 = df['Close'].ewm(span=12, adjust=False).mean()
    exp2 = df['Close'].ewm(span=26, adjust=False).mean()
    df['MACD'] = exp1 - exp2
    df['Signal_Line'] = df['MACD'].ewm(span=9, adjust=False).mean()

    # Bollinger Bands
    df['BB_middle'] = df['Close'].rolling(window=20).mean()
    df['BB_upper'] = df['BB_middle'] + 2 * df['Close'].rolling(window=20).std()
    df['BB_lower'] = df['BB_middle'] - 2 * df['Close'].rolling(window=20).std()

    return df

def calculate_rsi(prices, period=14):
    """Calculate Relative Strength Index"""
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def create_price_chart(df, symbol):
    """Create an interactive price chart with indicators"""
    # Create figure with secondary y-axis
    fig = make_subplots(
        rows=3, 
        cols=1, 
        shared_xaxes=True,
        vertical_spacing=0.1,  # Increased spacing between subplots
        row_heights=[0.5, 0.25, 0.25]  # Adjusted height ratios
    )

    # Main price chart
    fig.add_trace(
        go.Candlestick(
            x=df.index,
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['Close'],
            name='Price',
            showlegend=True
        ),
        row=1, col=1
    )

    # Bollinger Bands with reduced opacity
    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df['BB_upper'],
            name='Upper Band',
            line=dict(color='rgba(173, 204, 255, 0.3)'),
            showlegend=True
        ),
        row=1, col=1
    )

    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df['BB_lower'],
            name='Lower Band',
            line=dict(color='rgba(173, 204, 255, 0.3)'),
            fill='tonexty',
            fillcolor='rgba(173, 204, 255, 0.1)',
            showlegend=True
        ),
        row=1, col=1
    )

    # Moving averages with clearer colors
    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df['SMA_20'],
            name='20-Day MA',
            line=dict(color='#00FF9D', width=1.5),
            showlegend=True
        ),
        row=1, col=1
    )

    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df['SMA_50'],
            name='50-Day MA',
            line=dict(color='#FF4B4B', width=1.5),
            showlegend=True
        ),
        row=1, col=1
    )

    # Volume bars with improved colors
    colors = ['#4BFF4B' if row['Close'] >= row['Open'] else '#FF4B4B' 
              for index, row in df.iterrows()]

    fig.add_trace(
        go.Bar(
            x=df.index,
            y=df['Volume'],
            name='Volume',
            marker_color=colors,
            opacity=0.8,
            showlegend=True
        ),
        row=2, col=1
    )

    # RSI with improved visualization
    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df['RSI'],
            name='RSI',
            line=dict(color='#00FF9D', width=1.5),
            showlegend=True
        ),
        row=3, col=1
    )

    # Add RSI levels with labels
    fig.add_hline(
        y=70, 
        line_color='#FF4B4B', 
        line_width=1, 
        line_dash='dash',
        annotation_text="Overbought (70)",
        annotation_position="right",
        row=3, col=1
    )

    fig.add_hline(
        y=30, 
        line_color='#4BFF4B', 
        line_width=1, 
        line_dash='dash',
        annotation_text="Oversold (30)",
        annotation_position="right",
        row=3, col=1
    )

    # Update layout with improved styling
    fig.update_layout(
        template='plotly_dark',
        paper_bgcolor='#1E1E1E',
        plot_bgcolor='#2D2D2D',
        xaxis_rangeslider_visible=False,
        height=800,
        showlegend=True,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01,
            bgcolor='rgba(0,0,0,0.5)'
        ),
        margin=dict(l=50, r=50, t=30, b=50)
    )

    # Add grid and improve axes
    fig.update_xaxes(
        showgrid=True,
        gridwidth=1,
        gridcolor='rgba(128,128,128,0.2)',
        zeroline=False
    )

    fig.update_yaxes(
        showgrid=True,
        gridwidth=1,
        gridcolor='rgba(128,128,128,0.2)',
        zeroline=False
    )

    # Update y-axes labels with improved styling
    fig.update_yaxes(title_text="Price", row=1, col=1, title_standoff=10)
    fig.update_yaxes(title_text="Volume", row=2, col=1, title_standoff=10)
    fig.update_yaxes(title_text="RSI", row=3, col=1, title_standoff=10)

    return fig

def format_number(number):
    """Format large numbers with K, M, B suffixes"""
    try:
        if pd.isna(number) or number == 0:
            return "N/A"
        if number >= 1e9:
            return f"{number/1e9:.2f}B"
        elif number >= 1e6:
            return f"{number/1e6:.2f}M"
        elif number >= 1e3:
            return f"{number/1e3:.2f}K"
        return f"{number:.2f}"
    except:
        return "N/A"

def get_stock_news(symbol):
    """Get latest news for the stock"""
    try:
        company_symbol = symbol.replace('.NS', '')
        stock = yf.Ticker(symbol)
        news = stock.news

        news_data = []
        for item in news[:5]:  # Get latest 5 news items
            news_data.append({
                'Title': item['title'],
                'Date': datetime.fromtimestamp(item['providerPublishTime']).strftime('%Y-%m-%d'),
                'Link': item['link']
            })

        return pd.DataFrame(news_data)
    except Exception as e:
        print(f"Error fetching news: {str(e)}")
        return pd.DataFrame(columns=['Title', 'Date', 'Link'])

def get_company_profile(info):
    """Format company profile information"""
    profile = {
        'Business Summary': info.get('longBusinessSummary', 'N/A'),
        'Sector': info.get('sector', 'N/A'),
        'Industry': info.get('industry', 'N/A'),
        'Website': info.get('website', 'N/A'),
        'Full Time Employees': format_number(info.get('fullTimeEmployees', 0)),
    }
    return profile

def get_financial_metrics(info):
    """Get key financial metrics"""
    currency_symbol = '₹' if '.NS' in info.get('symbol', '') else '$'
    metrics = {
        'Market Cap': f"{currency_symbol}{format_number(info.get('marketCap', 0))}",
        'P/E Ratio': format_number(info.get('trailingPE', 0)),
        'EPS (TTM)': f"{currency_symbol}{format_number(info.get('trailingEps', 0))}",
        'Beta': format_number(info.get('beta', 0)),
        'Dividend Yield': f"{format_number(info.get('dividendYield', 0) * 100)}%" if info.get('dividendYield') else 'N/A',
        'Revenue (TTM)': f"{currency_symbol}{format_number(info.get('totalRevenue', 0))}",
        'Profit Margin': f"{format_number(info.get('profitMargins', 0) * 100)}%",
        'Operating Margin': f"{format_number(info.get('operatingMargins', 0) * 100)}%",
        'ROE': f"{format_number(info.get('returnOnEquity', 0) * 100)}%",
        'ROA': f"{format_number(info.get('returnOnAssets', 0) * 100)}%",
        'Debt to Equity': format_number(info.get('debtToEquity', 0)),
        'Current Ratio': format_number(info.get('currentRatio', 0)),
    }
    return metrics
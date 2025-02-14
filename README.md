# Indian Stock Analysis Dashboard

A comprehensive stock analysis dashboard built with Streamlit, providing real-time analysis of Indian stocks with interactive visualizations and detailed company information.

## Features
- Real-time stock price tracking for Indian stocks
- Interactive technical analysis charts with multiple indicators
- Company profile and ESG scores
- Financial metrics and ratios
- Latest stock-specific news
- Custom date range analysis
- Market status indicators

## Project Structure
- `main.py`: Main application file containing the Streamlit dashboard interface
- `utils.py`: Utility functions for data processing and chart creation
- `styles.css`: Custom styling for the dashboard
- `.streamlit/config.toml`: Streamlit configuration file

## Technical Stack
- **Frontend**: Streamlit
- **Data Processing**: Pandas, NumPy
- **Data Visualization**: Plotly
- **Stock Data**: yfinance
- **News Scraping**: trafilatura

## Installation and Setup
1. Clone the repository
2. Install dependencies:
```bash
pip install streamlit pandas numpy plotly yfinance trafilatura
```
3. Run the application:
```bash
streamlit run main.py
```

## Usage
1. Select a stock from the sidebar dropdown
2. Choose a time period or set a custom date range
3. Click "Analyze Stock" to view detailed analysis
4. Navigate through different tabs for various metrics and information

## Features Explanation
1. **Technical Analysis**
   - Candlestick chart with Bollinger Bands
   - Moving averages (20-day and 50-day)
   - Volume analysis
   - RSI indicator

2. **Company Profile**
   - Business summary
   - Industry information
   - ESG scores
   - Company contact details

3. **Financial Metrics**
   - Key ratios and metrics
   - Market performance indicators
   - Profitability metrics

4. **News Integration**
   - Latest company news
   - Real-time updates

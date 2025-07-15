import asyncio
import logging
import pprint
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass

import pandas as pd
import yfinance as yf


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
pd.set_option('display.width', 120)
pd.set_option('display.max_columns', 15)
pd.set_option('display.max_rows', 10)


@dataclass
class OptionChain:
    """A structured, type-safe container for option chain data."""
    calls: pd.DataFrame
    puts: pd.DataFrame
    expiration_date: str


class FinanceTool:
    """
    A fully encapsulated, asynchronous, report-generating financial tool.

    Each public method is a self-contained unit that performs data fetching,
    comprehensive validation, and formatting, returning a structured string
    ready for inclusion in a final report.
    """

    def __init__(self):
        """Initializes the FinanceTool with a ticker cache."""
        self._ticker_cache: Dict[str, yf.Ticker] = {}
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.info("FinanceTool (Fully Encapsulated Mode) initialized.")
        

    # --- PRIVATE, SELF-CONTAINED HELPER METHODS ---

    def _get_ticker(self, ticker: str) -> Optional[yf.Ticker]:
        ticker_upper = ticker.upper()
        if ticker_upper in self._ticker_cache:
            return self._ticker_cache[ticker_upper]
        stock = yf.Ticker(ticker_upper)
        if stock.history(period="1d").empty:
            self.logger.error(f"Ticker '{ticker_upper}' is invalid or has no data.")
            return None
        self._ticker_cache[ticker_upper] = stock
        return stock

    async def _run_blocking(self, func, *args, **kwargs) -> Any:
        try:
            return await asyncio.to_thread(func, *args, **kwargs)
        except Exception as e:
            self.logger.error(f"A yfinance call failed: {e}", exc_info=False)
            return None

    def _format_data(self, data: Any, title: str) -> str:
        """Universal private helper to format any data into a titled string block."""
        header = f"--- {title} ---"
        if data is None: return f"{header}\nData not available."
        if isinstance(data, pd.DataFrame) and data.empty: return f"{header}\nData not available."
        if isinstance(data, (list, tuple)) and not data: return f"{header}\nData not available."
        
        if isinstance(data, (pd.DataFrame, pd.Series)): return f"{header}\n{data.to_string()}"
        if isinstance(data, (dict, list)): return f"{header}\n{pprint.pformat(data, indent=2, width=80)}"
        return f"{header}\n{str(data)}"

    # --- PUBLIC, SELF-CONTAINED REPORT-GENERATING METHODS ---

    async def get_info(self, ticker: str) -> str:
        """Fetches, validates, and formats core company information into a string."""
        title = f"Core Information for {ticker}"
        if not (stock := self._get_ticker(ticker)): return self._format_data(None, title)
        
        data = await self._run_blocking(lambda: stock.info)

        if data and isinstance(data, dict):
            report_sample = {
                "Company Name": data.get('longName'),
                "Sector": data.get('sector'),
                "Market Cap": f"${data.get('marketCap', 0):,}",
                "P/E Ratio": data.get('trailingPE'),
                "Dividend Yield": f"{data.get('dividendYield', 0) * 100:.2f}%"
            }
            return self._format_data(report_sample, title)
        return self._format_data(None, title)

    async def get_news(self, ticker: str) -> str:
        """Fetches, validates, and formats the latest news headline into a string."""
        title = f"Latest News for {ticker}"
        if not (stock := self._get_ticker(ticker)): return self._format_data(None, title)
        
        data = await self._run_blocking(lambda: stock.news)
        if data and isinstance(data, list):
            headline = data[0].get('content', {}).get('title', 'No title in news content.')
            return self._format_data(headline, title)
        return self._format_data(None, title)

    async def get_financials(self, ticker: str, quarterly: bool = False) -> str:
        """Fetches, validates, and formats the income statement into a string."""
        period = "Quarterly" if quarterly else "Annual"
        title = f"{period} Income Statement for {ticker}"
        if not (stock := self._get_ticker(ticker)): return self._format_data(None, title)
        
        df = await self._run_blocking(lambda: stock.quarterly_financials if quarterly else stock.financials)
        return self._format_data(df, title)

    async def get_balance_sheet(self, ticker: str, quarterly: bool = False) -> str:
        """Fetches, validates, and formats the balance sheet into a string."""
        period = "Quarterly" if quarterly else "Annual"
        title = f"{period} Balance Sheet for {ticker}"
        if not (stock := self._get_ticker(ticker)): return self._format_data(None, title)

        df = await self._run_blocking(lambda: stock.quarterly_balance_sheet if quarterly else stock.balance_sheet)
        return self._format_data(df, title)

    async def get_cash_flow(self, ticker: str, quarterly: bool = False) -> str:
        """Fetches, validates, and formats the cash flow statement into a string."""
        period = "Quarterly" if quarterly else "Annual"
        title = f"{period} Cash Flow for {ticker}"
        if not (stock := self._get_ticker(ticker)): return self._format_data(None, title)

        df = await self._run_blocking(lambda: stock.quarterly_cashflow if quarterly else stock.cashflow)
        return self._format_data(df, title)

    async def get_history(self, ticker: str, period: str = "1y") -> str:
        """Fetches, validates, and formats recent price history into a string."""
        title = f"Price History for {ticker} (Last 5 days of {period})"
        if not (stock := self._get_ticker(ticker)): return self._format_data(None, title)
        
        df = await self._run_blocking(stock.history, period=period)
        return self._format_data(df.tail() if isinstance(df, pd.DataFrame) else None, title)
        
    async def get_major_holders(self, ticker: str) -> str:
        """Fetches, validates, and formats major holder data into a string."""
        title = f"Major Holders for {ticker}"
        if not (stock := self._get_ticker(ticker)): return self._format_data(None, title)
        
        df = await self._run_blocking(lambda: stock.major_holders)
        return self._format_data(df, title)

    async def get_institutional_holders(self, ticker: str) -> str:
        """Fetches, validates, and formats institutional holder data into a string."""
        title = f"Top Institutional Holders for {ticker}"
        if not (stock := self._get_ticker(ticker)): return self._format_data(None, title)
        
        df = await self._run_blocking(lambda: stock.institutional_holders)
        return self._format_data(df.head() if isinstance(df, pd.DataFrame) else None, title)

    async def get_recommendations(self, ticker: str) -> str:
        """Fetches, validates, and formats analyst recommendations into a string."""
        title = f"Analyst Recommendations for {ticker} (Last 5)"
        if not (stock := self._get_ticker(ticker)): return self._format_data(None, title)

        df = await self._run_blocking(lambda: stock.recommendations)
        return self._format_data(df.tail() if isinstance(df, pd.DataFrame) else None, title)

    async def get_sustainability(self, ticker: str) -> str:
        """Fetches, validates, and formats ESG ratings into a string."""
        title = f"ESG Sustainability Ratings for {ticker}"
        if not (stock := self._get_ticker(ticker)): return self._format_data(None, title)
        
        df = await self._run_blocking(lambda: stock.sustainability)
        return self._format_data(df, title)
        
    async def get_option_expirations(self, ticker: str) -> str:
        """Fetches, validates, and formats option expiration dates into a string."""
        title = f"Option Expiration Dates for {ticker} (First 10)"
        if not (stock := self._get_ticker(ticker)): return self._format_data(None, title)

        exp_tuple = await self._run_blocking(lambda: stock.options)
        return self._format_data(exp_tuple[:10] if exp_tuple else None, title)

    async def get_option_chain(self, ticker: str) -> str:
        """Fetches, validates, and formats the full option chain into a string."""
        title = f"Option Chain Report for {ticker}"
        if not (stock := self._get_ticker(ticker)): return self._format_data(None, title)

        expirations = await self._run_blocking(lambda: stock.options)
        if not expirations: return self._format_data(None, title)
        target_expiration_date = expirations[0]

        raw_chain_obj = await self._run_blocking(stock.option_chain, target_expiration_date)
        if raw_chain_obj is None or (raw_chain_obj.calls.empty and raw_chain_obj.puts.empty):
            return self._format_data(None, title)
        
        chain_obj = OptionChain(
            calls=raw_chain_obj.calls,
            puts=raw_chain_obj.puts,
            expiration_date=target_expiration_date
        )

        exp_date_str = f"Expiration Date: {chain_obj.expiration_date}"
        calls_report = self._format_data(chain_obj.calls.tail(3), "Sample Calls")
        puts_report = self._format_data(chain_obj.puts.tail(3), "Sample Puts")
        return f"--- {title} ---\n{exp_date_str}\n\n{calls_report}\n\n{puts_report}"

    async def get_all_tools(self):
        return [
            self.get_info,
            self.get_news,
            self.get_financials,
            self.get_balance_sheet,
            self.get_cash_flow,
            self.get_history,
            self.get_major_holders,
            self.get_institutional_holders,
            self.get_recommendations,
            self.get_sustainability,
            self.get_option_expirations,
            self.get_option_chain
        ]


async def main():
    """
    Demonstrates the power of the fully encapsulated FinanceTool.
    This function is now extremely clean, as all logic is hidden
    inside the tool's methods.
    """
    tool = FinanceTool()
    ticker = "AAPL"

    print("\n" + "="*80)
    print(f"      GENERATING FULL SELF-CONTAINED REPORT FOR: {ticker}")
    print("="*80 + "\n")
    
    report_parts = await asyncio.gather(
        tool.get_info(ticker),
        tool.get_news(ticker),
        tool.get_financials(ticker, quarterly=True),
        tool.get_balance_sheet(ticker, quarterly=True),
        tool.get_cash_flow(ticker, quarterly=True),
        tool.get_history(ticker),
        tool.get_major_holders(ticker),
        tool.get_institutional_holders(ticker),
        tool.get_recommendations(ticker),
        tool.get_sustainability(ticker),
        tool.get_option_expirations(ticker),
        tool.get_option_chain(ticker)
    )

    for part in report_parts:
        print(part)
        print("\n" + "-"*60 + "\n")

if __name__ == "__main__":
    asyncio.run(main())
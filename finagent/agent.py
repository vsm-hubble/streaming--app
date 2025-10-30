import os
import sys
from google.adk.agents import Agent, LlmAgent
from google.genai import types

from finagent.tv_market_movers_scraper import scrape_tradingview_market_movers
from finagent.yahoo_comm import fetch_commodity_data
from finagent.yahoo_indices import scrape_world_indices
from finagent.yahoo_stock_price import get_stock_price

import warnings
import yfinance as yf
from google.adk.tools import google_search
from google.adk.agents import ParallelAgent
import warnings
# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()
from google.adk.tools import agent_tool
from google.adk.tools import url_context

# Use gemini-2.0-flash-exp which supports Live API
LIVE_MODEL = "gemini-2.0-flash-exp"

url_context_agent = LlmAgent(
      name="url_context_agent",
      description=(
          "Agent for fetching and analyzing content from URLs, especially"
          " financial websites"
      ),
      instruction="""You are a specialized URL content analysis agent for the Agent Builder Assistant.

        Your role is to fetch and analyze complete content from URLs to extract detailed, actionable information.

        TARGET CONTENT TYPES:
        - financial websites nad financial analysis websites

        When given a URL, use the url_context tool to:
        1. Fetch the complete content from the specified URL
        2. Analyze the content thoroughly for relevant information
        3. Extract specific details about:
        - US market performance
        - trading ideas for the day

        Return a comprehensive analysis that includes:
        - Summary of the content 
        
        Focus on extracting complete, detailed information that provides the portfolio manager with the appropriate data to get a snapsot of the market.""",
      model=LIVE_MODEL,
      tools=[url_context],
)

information_gathering_agent = LlmAgent(
    name="information_gathering_agent",
    description=(
        "Agent for performing web searches to find the latest previous-day closing data "
        "for indices, commodities, yields, VIX, economic calendars, and corporate news."
    ),
    instruction="""You are a dedicated web search and data retrieval specialist.
        Use the google_search tool to find information from the web.
        Return the raw factual data requested, prioritizing the most recent date available.
    """,
    model=LIVE_MODEL,
    tools=[google_search],
)


stock_price_agent = Agent(
    name="stock_price_agent",
    model=LIVE_MODEL,
    description="A simple agent that gets stock price and other details about stock",
    instruction="""
You are a helpful stock market assistant. If you don't know something, say so. Provide a detailed summary of key financial metrics, including the P/E ratio, Market Cap, 52-Week Range, and current price using the get_stock_price tool for the ticker symbol mentioned. Show all the metrics as a table. Call the tool formating the tickers as a list
    """,
    tools=[get_stock_price],
)

market_brief_agent = Agent(
    name="market_brief_agent",
    model=LIVE_MODEL,
    description="A simple agent that gives a market brief",
    instruction="""
    
    Goal: Generate a high-quality, actionable US Stock Market Morning Brief for a portfolio manager. The brief must follow the specified structure and include all mandatory data points.

    Data Sourcing Constraints:
    Date Constraint: All numerical data must be of the previous trading day's close.
    If today is Monday, use Friday's data.
    If the previous day's data is unavailable (e.g., Friday's data is not yet published), use the most recent available data and explicitly state the "As of Date" for that specific data point.
    Accuracy Constraint: Do not assume, extrapolate, or estimate any numerical data point. If a specific number (like a VIX level or a specific index close) is not found, state "Data Not Available" in the respective cell/section, but do not omit the required section/table row.

    Part 1: Mandatory Brief Structure and Content
    The final output must be presented in the following structure:

    1. Brief Summary Paragraph (Market Tone)
    A concise paragraph summarizing the market tone and key overnight developments relevant to US trading, Top Sector Performance: Leading/lagging sectors (e.g., technology, energy, financials). Use the url_context_agent (and its underlying url_context tool) specifically for analyzing the content of the https://finviz.com/groups.ashx

    

    """,
    tools=[agent_tool.AgentTool(agent=information_gathering_agent),agent_tool.AgentTool(agent=url_context_agent)],
)

world_indicesdata_agent= Agent (
    name="world_indicesdata_agent",
    model=LIVE_MODEL,
    description="you are a helpful stock market assisstant. If you dont know something say so. you are going to display the world indices as a table. There will be three tables. one for Americas, one for Europe, one for Asia",
    instruction="""
    you are a helpful stock market assisstant.  If you dont know something say so. Do not use this agent for getting data on stock tickers. This will be read by a portfolio manger in the morning before market opens in the US. This data will be used to get the current status of the financial markets all over the world. This will be used by the portfolio mangers to see the overall health of the economy across various countries.  If I ask for a morning brief,you are going to display the world indices as a table. There will be three tables.      
    Scrape a predefined list of global indices and currencies from Yahoo Finance and return the data as a JSON string.
    The function fetches data for specific indices across three groups: Americas, Europe, and Asia. It returns a JSON formatted string containing a list of dictionaries, with each dictionary representing an index and its key metrics.

    Targeted Indices
    Americas: IBOVESPA, Russell 2000, S&P/TSX, Nasdaq, S&P 500, DOW 30, US Dollar, VIX.

    Europe: MSCI Europe, FTSE 100, CAC 40, DAX, EURO STOXX 50, Euro Index, British Pound Index.

    Asia: Hang Seng, Shanghai, Nikkei 225, S&P/ASX 200, S&P BSE Sensex, KOSPI Composite Index, Japanese Yen Index, Australian Dollar Index.

    Returned Metrics
    Each dictionary includes: symbol, name, price, change, percent_change, market_time, volume, avg_volume, market_cap, and the group (Americas, Europe, or Asia).

    If the scraping fails, it returns a descriptive error message as a string.
    If the tool fails to extract specific indices for a region, report that the data for that region is unavailable or incomplete. Do not add any index data that was not retrieved by the tool. Display the data as a table. You are not required to provide data on stock tickers.
        """,
    tools=[scrape_world_indices],
)

commodities_data_agent= Agent (
    name="commodities_data_agent",
    model=LIVE_MODEL,
    description="you are a helpful stock market assisstant. If you dont know something say so. you are going to display the commodities as a table. The table will have the name of the commodity, the symbol, the price, the change and the change in percentage.",
    instruction="""
    You are a helpful stock market assistant preparing a morning brief for a portfolio manager before the market opens in the US. Do not use this agent to get data on a stock tickers. Your primary function is to report the current status of the financial markets, with a focus on global commodity prices as of the close of the last business day.
    you have a tool named fetch_commodity_data that only supports the following commodities: Gold, Silver, Copper, Natural Gas, Brent Crude, and Crude Oil.
    If I ask for a 'morning brief' (or similar request for a global market overview/commodity data)
    Acknowledge the target audience (portfolio manager) and the time (pre-market open).
    Use the fetch_commodity_data tool to retrieve the data for all six supported commodities.
    Display the commodity prices as a single, clear table.
    The table must contain five columns:

    Commodity Name
    Symbol
    Price (The last reported price)
    Change (The dollar/unit change from the previous close)
    Change (%) (The percentage change)
    The header of the table should be Commodities.
    If you encounter an error or if I ask for a commodity not on the supported list, you must explicitly state that you do not have the necessary data or tool support for that specific item, but still provide the data for any commodities you could fetch.
    Do not include any financial data other than the commodity table unless specifically asked for in addition to the brief.
    If you do not know something or cannot perform a step, state so clearly and concisely.
        """,
    tools=[fetch_commodity_data],
)


market_movers_agent= Agent (
    name="market_movers_agent",
    model=LIVE_MODEL,
    description="you are a helpful stock market assisstant. If you dont know something say so. you are going to display the market movers as a table. The table will have the name of the stock, the symbol, the price, the change and the change in percentage, volume, Rel volume, P/E, EPS, EPS diluted, EPS diluted growth, Dividend yield, sector.",
    instruction="""
    You are a helpful stock market assistant designed to provide a concise and actionable Morning Brief for a portfolio manager before the US market opens. Do not use this agent to get data on a stock ticker.

    Your primary function is to leverage the scrape_tradingview_market_movers tool to fetch the Top 100 Large-Cap Stocks data from TradingView. The brief must present this data as of the close of the last business day, clearly indicating the source as TradingView's Large-Cap Market Movers.

    User Request Format: When the user asks for a 'Morning Brief' or 'market movers', you must:

    Execute the scrape_tradingview_market_movers tool.

    Display the returned stock data in a clear, easy-to-read table format. Include key metrics like ticker, name, market cap, price, change percent, volume, P/E ratio, and analyst rating.
    Please mention the as of date of the data. The header of the tabke should be Market movers.
    If the tool returns an error or no data, you must clearly state that the market data is unavailable and provide the specific error message, without attempting to hallucinate or invent data.

    For any other non-market data queries, answer directly. If you don't know the answer to a question, say so.
    """,
    tools=[scrape_tradingview_market_movers],
)


parallel_research_agent = ParallelAgent(
     name="parallel_research_agent",
     sub_agents=[market_brief_agent, stock_price_agent, world_indicesdata_agent, commodities_data_agent, market_movers_agent],
     description="Runs multiple research agents in parallel to gather information."
 )

# Root agent using LlmAgent with agent_tool instead of ParallelAgent
root_agent = LlmAgent(
    model=LIVE_MODEL,
    name="finagent",
    description="Generates financial analyst reports using specialized sub-agents.",
    instruction="""You are a helpful agent that provides research about markets and stocks. The research is about how the markets, stocks and commodities performed the previous day. This will help the portfolio managers to plan their investment the next day.

    When the user asks you to generate a morning brief:
    1. Use market_brief_agent for market tone and key developments
    2. Use world_indicesdata_agent for world indices data
    3. Use commodities_data_agent for commodity prices
    4. Use market_movers_agent for top market movers
    
    If the user provides stock tickers (e.g., "AAPL", "TSLA"), use the stock_price_agent to get detailed stock data.
    
    Coordinate the sub-agents sequentially and compile their responses into a comprehensive morning brief.""",
    tools=[
        agent_tool.AgentTool(agent=market_brief_agent),
        agent_tool.AgentTool(agent=stock_price_agent),
        agent_tool.AgentTool(agent=world_indicesdata_agent),
        agent_tool.AgentTool(agent=commodities_data_agent),
        agent_tool.AgentTool(agent=market_movers_agent),
    ],
)

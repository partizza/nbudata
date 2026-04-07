from exchange import get_rates
from datetime import date, datetime

from typing import Any

from mcp.server.fastmcp import FastMCP

# Create an MCP server
mcp = FastMCP("NBU data", json_response=True)


@mcp.tool(name="nbu_exchange_rate",
          description="Retrieves National Bank of Ukraine exchange rates for given currency and period in json format")
def nbu_exchange_rate(base_currency: str, date_from: str, date_to: str) -> list[dict[str, Any]]:
    """
        Retrieves National Bank of Ukraine exchange rates for given currency and period.

    :param base_currency: ISO3 currency code
    :param date_from: date from which exchange rate is retrieved in format YYYY-MM-DD
    :param date_to: date to which exchange rate is retrieved in format YYYY-MM-DD
    :return: json with exchange rates
    """

    date_from: date = datetime.strptime(date_from, "%Y-%m-%d").date()
    date_to: date = datetime.strptime(date_to, "%Y-%m-%d").date()

    return get_rates(base_currency, date_from, date_to)


if __name__ == "__main__":
    mcp.run(transport="stdio")

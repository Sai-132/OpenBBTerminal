"""Onclusive Data Model"""

import logging
import requests
import pandas as pd

from openbb_terminal.decorators import check_api_key, log_start_end
from openbb_terminal.rich_config import console
from openbb_terminal.core.session.current_user import get_current_user

logger = logging.getLogger(__name__)

@log_start_end(log=logger)
@check_api_key(["API_ALTHUB_TOKEN"])
def get_data(
    ticker: str = "",
    start_date: str = "",
    end_date: str = "",
    date: str = "",
    limit: int = 100,
    offset: int = 0,
) -> pd.DataFrame:

    """Getting Onclusive Data. [Source: Invisage Plotform]

    Parameters
    ----------
    ticker : str
        Stock ticker
    start_date : str
        Records are coming from this day (Start date in YYYY-MM-DD format)
    end_date : str
        Records will get upto this day (End date in YYYY-MM-DD format)
    date : str
        Show that the records on this day (date in YYYY-MM-DD format)
    limit: int
        The number of records to get
    offset : int
        The number of records to offset
    """

    headers = {
        "accept": "application/json",
        "Authorization": f"token {get_current_user().credentials.API_ALTHUB_TOKEN}",
    }

    df = pd.DataFrame(data=None)

    query_params = {
        "all_feilds": 'False',
        "ordering":"-published_on,-share_of_article,-pagerank"
    }
    if ticker:
        query_params["ticker"] = ticker
    if start_date:
        query_params["published_on__gte"] = start_date
    if end_date:
        query_params["published_on__lte"] = end_date

    if start_date and end_date and not date:
        if start_date > end_date:
            console.print("start_date must be less than end_date")
            return df

    if date:
        query_params["published_on"] = date
        if start_date:
            del query_params["published_on__gte"]
        if end_date:
            del query_params["published_on__lte"]

    if limit:
        query_params["limit"] = limit
    if offset:
        query_params["offset"] = offset

    response = requests.get(
        "https://althub-backend.invisagealpha.com/api/OnclusiveSentiment/",
        headers=headers,
        params=query_params,
    ).json()
    df = pd.DataFrame(data=response["results"])
    df['adjusted_sentiment'] = df['adjusted_sentiment'].astype(float)

    def condition(x):
        if x >= 250:
            return "Super Positive"
        elif x<250 and x>0:
            return "Positive"
        elif x == 0:
            return "Neutral"
        elif x <0 and x> -250:
            return "Negative"
        else:
            return "Super Negative"

    sentiment = {50:"Positive",-50:"Negative",0:"Neutral"}

    if not df.empty:
        df['raw_sentiment'] = df['raw_sentiment'].map(sentiment)
        df['adjusted_sentiment'] = df['adjusted_sentiment'].apply(condition)
    return df

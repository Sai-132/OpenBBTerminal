"""Onclusive Data Model"""

import logging

import json
import requests
import pandas as pd
import numpy as np
import datetime
import os

from openbb_terminal.decorators import log_start_end
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def get_data(
    ticker: str = "",
    start_date: str = "",
    end_date: str = "",
    date: str = "",
    limit: int = 100,
    offset: int = 0,
) -> pd.DataFrame:
    API_TOKEN = os.getenv("ALTHUB_API_TOKEN")

    headers = {"accept": "application/json", "Authorization": f"token {API_TOKEN}"}

    df = pd.DataFrame(data=None)

    query_params = {}
    if ticker:
        query_params["ticker"] = ticker
    if start_date:
        query_params["published_on__gte"] = start_date
    if end_date:
        query_params["published_on__lte"] = end_date

    if start_date and end_date and not date:
        if start_date > end_date:
            console.print("start_date must be lessthan end_date")
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
        f"https://althub-backend.invisagealpha.com/api/OnclusiveSentiment/?all_feilds=flase&ordering=-published_on,-share_of_article,-pagerank",
        headers=headers,
        params=query_params,
    ).json()
    df = pd.DataFrame(data=response["results"])

    return df

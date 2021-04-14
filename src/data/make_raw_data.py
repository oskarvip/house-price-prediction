# -*- coding: utf-8 -*-
import logging
from pathlib import Path
from dotenv import find_dotenv, load_dotenv
import requests
from hashlib import sha1
import random
import string
import time
import os
import json
import datetime
from dateutil.relativedelta import relativedelta


def main():
    """Fetches raw data from the Booli API, saves the data in ../raw."""
    logger = logging.getLogger(__name__)
    limit = input("Please select results limit (Default = All): ") or None
    query = (
        input("Please input a search query (Default = Sverige): ") or "Sverige"
    ).lower()
    min_sold_date = input("Please input a minimum sales date (Default = Today - 1 year): ") or (
        datetime.date.today() - relativedelta(years=1)
    ).strftime("%Y%m%d")
    max_sold_date = input(
        "Please input a maximum sales date (Default = Today): "
    ) or datetime.date.today().strftime("%Y%m%d")
    offset = input("Please select request offset (Default = 0): ") or 0

    logger.info(
        f"requesting raw data from the Booli api with parameters: (query: {query}, min_sold_date: {min_sold_date}, "
        f"max_sold_date: {max_sold_date}, limit: {limit}, offset: {offset})"
    )
    booli = Booli(api_key=BOOLI_API_KEY, caller_id=BOOLI_CALLER_ID)

    file_path = Path().absolute().parents[1].joinpath(Path("data/raw"))
    file_name = (
        f"{min_sold_date}-{datetime.date.today().strftime('%Y%m%d')}_{query}.json"
    )
    with open(file_path.joinpath(file_name), "a") as out_file:
        # print(Path.absolute().joinpath(Path.parent))
        while True:
            try:
                data = booli.get_sold(
                    query=query,
                    limit=limit,
                    min_sold_date=min_sold_date,
                    max_sold_date=max_sold_date,
                    offset=offset,
                )
                logger.info(
                    f"Query yielded {data['totalCount']} results, retrieved {data['count']} rows from Booli"
                )
            except requests.HTTPError as e:
                logger.error(f"Error when requesting data from Booli: {e}")
            json.dump(obj=data, fp=out_file, ensure_ascii=False)
            offset += data["count"]
            amount_of_objects = data["totalCount"]
            if not limit:
                limit = amount_of_objects
            if offset > amount_of_objects:
                break


class Booli:
    """
    Class for managing requests to the Booli API.
    User must specify a Booli API Key and a Caller ID (Contact Booli at api@booli.se to get it).
    """

    def __init__(self, api_key, caller_id):
        self.caller_id = caller_id
        self.api_key = api_key

    def get_sold(
        self, query, limit=None, offset=None, min_sold_date=None, max_sold_date=None
    ):
        """
        Requests data from the Booli API "sold" endpoint.
        """
        ts = int(time.time())
        unique = "".join(
            random.choice(string.ascii_uppercase + string.digits) for _ in range(16)
        )
        hash_str = sha1(
            (self.caller_id + str(ts) + self.api_key + unique).encode("utf-8")
        ).hexdigest()
        parameters = {
            "callerId": self.caller_id,
            "time": ts,
            "unique": unique,
            "hash": hash_str,
            "q": query,
            "limit": limit,
            "offset": offset,
            "minSoldDate": min_sold_date,
            "maxSoldDate": max_sold_date,
        }
        print(parameters)
        response = requests.get("https://api.booli.se/sold", params=parameters)
        if response.status_code == 200:
            return response.json()
        else:
            raise requests.HTTPError(
                {
                    "response_code": response.status_code,
                    "response_message": response.content.decode(),
                }
            )


if __name__ == "__main__":
    log_fmt = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    # not used in this stub but often useful for finding various files
    project_dir = Path(__file__).resolve().parents[2]

    # find .env automagically by walking up directories until it's found, then
    # load up the .env entries as environment variables
    load_dotenv(find_dotenv())

    BOOLI_API_KEY = os.environ["BOOLI_API_KEY"]
    BOOLI_QUERY = os.environ["BOOLI_QUERY"]
    BOOLI_CALLER_ID = os.environ["BOOLI_CALLER_ID"]

    main()

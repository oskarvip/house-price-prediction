# -*- coding: utf-8 -*-
import click
import logging
from pathlib import Path
from dotenv import find_dotenv, load_dotenv
import requests
from hashlib import sha1
import random
import string
import time
import os


@click.command()
@click.argument("input_filepath", type=click.Path(exists=True))
@click.argument("output_filepath", type=click.Path())
def main(input_filepath, output_filepath):
    """Runs data processing scripts to turn raw data from (../raw) into
    cleaned data ready to be analyzed (saved in ../processed).
    """
    logger = logging.getLogger(__name__)
    logger.info("making final data set from raw data")
    booli = Booli(api_key=BOOLI_API_KEY, caller_id=BOOLI_CALLER_ID)

    data = booli.get_booli_data(query="Uddevalla", limit=100)
    print(data)


class Booli:
    """
    Class for managing requests to the Booli API.
    User must specify a Booli API Key (Contact Booli to get one) and a Caller ID (Choose an identifier for your app).
    """

    def __init__(self, api_key, caller_id):
        self.caller_id = caller_id
        self.api_key = api_key

    def get_booli_data(
        self, query, limit=1000, offset=None, min_sold_date=None, max_sold_date=None
    ):
        """
        Requests data from the Booli API.
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

        response = requests.get("https://api.booli.se/sold", params=parameters)

        # print (response.status_code)
        # print (response.content.decode("utf-8"))

        # data = json.loads(response.content.decode("utf-8"))
        data = response.json()
        # sold = data["sold"]
        return data


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

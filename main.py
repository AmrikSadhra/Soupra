from scraper import get_available_supras
from models import Supra
from mongoengine import connect
from pushbullet import API
from datetime import datetime
import logging
import sys
import os

logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.INFO, stream=sys.stdout,
                    datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger()


def check_env_vars():
    for env_var in ["PUSHBULLET_API_TOKEN", "MONGO_USER", "MONGO_PASSWORD", "HOME_POSTCODE"]:
        if env_var not in os.environ:
            logging.error("Please set the {} environment variable".format(env_var))
            exit(1)


# If registration doesn't exist in the DB, add the car
def commit_new_supras(available_supras_, pb_api_):
    for supra in available_supras_:
        if Supra.objects(registration__exact=supra.registration).count() == 0:
            logging.info("New Supra found: {}".format(supra))
            pb_api_.send_note("Supra Found", "{}".format(supra))
            supra.save()


# If we no longer have an available supra that matches a DB one, mark it as sold
def check_sold_supras(available_supras_, pb_api_):
    for db_supra in Supra.objects(sold__exact=False):
        found = False
        for avail_supra in available_supras_:
            if db_supra.registration == avail_supra.registration:
                found = True

        if not found:
            db_supra.sold = True
            db_supra.date_sold = datetime.now()
            db_supra.save()
            logging.info("Supra sold :( {}".format(db_supra))
            pb_api_.send_note("Supra Sold :(", "{}".format(db_supra))


def check_for_supras(pb_api_):
    connect(host="mongodb://{}:{}@hp-z220.lan:32788/scrapers".format(os.environ['MONGO_USER'],
                                                                     os.environ['MONGO_PASSWORD']))

    logging.info("Scraping Toyota Used vehicles")

    # Get list of active Supras from Toyota, lazy exception handling for the case that network is slower than timeouts
    try:
        available_supras = get_available_supras()
    except Exception as e:
        logging.error("Failed to scrape Toyota website: {}, exiting".format(e))
        exit(1)

    logging.info("Available Supras: {}".format(len(available_supras)))

    # Put any new ones in the DB
    commit_new_supras(available_supras, pb_api_)

    # Check if any were sold
    check_sold_supras(available_supras, pb_api_)


if __name__ == '__main__':
    check_env_vars()

    pb_api = API()
    pb_api.set_token(os.environ['PUSHBULLET_API_TOKEN'])

    check_for_supras(pb_api)

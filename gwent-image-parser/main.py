import json
import os
import sys
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from time import sleep
import re

valid_url = re.compile(
        r'^(?:http|ftp)s?://' # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
        r'localhost|' #localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?' # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)

valid_float = re.compile(r'[+-]?[0-9]+\.[0-9]+')

def validate_env(ENV, regex=None):
    value = os.environ.get(ENV)

    empty = not value or str(value).strip() == ""
    re_valid = True
    if (regex):
        re_valid = re.match(regex, value) is not None

    if (empty or not re_valid):
        print("Undeclared or invalid env variable: " + ENV)
        return None
    else:
        return value


if __name__ == "__main__":
    INPUT_DATA = validate_env("INPUT")
    OUTPUT_FOLDER = validate_env("OUTPUT")
    SCREENSHOT_TARGET = validate_env("TARGET")
    SERVICE_URL = validate_env("SERVICE_URL", valid_url)
    WAIT_LIMIT = float(validate_env("WAIT_LIMIT", valid_float))
    PAGE_WAIT_TIME = float(validate_env("PAGE_WAIT_TIME", valid_float))

    if (None in [INPUT_DATA, OUTPUT_FOLDER, SCREENSHOT_TARGET, SERVICE_URL]):
        sys.exit(1)

    if (not os.path.exists(INPUT_DATA)):
        print("Input data file doesn't exist.")
        sys.exit(1)

    if (not os.path.exists(OUTPUT_FOLDER)):
        try:
            os.mkdir(OUTPUT_FOLDER)
        except:
            print("Failed to create output folder.")
            sys.exit(1)

    try:
        cards = {}
        with open(INPUT_DATA, 'r', encoding='utf-8') as fp:
            cards = json.load(fp)

        dc = DesiredCapabilities.CHROME
        dc['goog:loggingPrefs'] = {'browser': 'ALL'}
        dc['acceptSslCerts'] = True
        dc['acceptInsecureCerts'] = True

        browser = None
        limit = WAIT_LIMIT

        while browser == None:
            try:
                browser = webdriver.Remote('http://chrome:4444/wd/hub', desired_capabilities=dc)
            except Exception as e:
                limit -= 1
                sleep(1)
                if (limit <= 0):
                    raise e

        progress = 0

        for card_name, card_info in cards.items():
            try:
                browser.get(SERVICE_URL + card_info['ingameId'])
            except:
                continue

            sleep(PAGE_WAIT_TIME)
            local_path = os.path.join(OUTPUT_FOLDER, card_info['ingameId'] + ".png")
            image = browser.find_element_by_css_selector(SCREENSHOT_TARGET).screenshot(local_path)
            progress += 1
            print(f"[{progress}/{len(cards.keys())}] Ready: {local_path}")
    except Exception as e:
        print("Error occured: ", e)
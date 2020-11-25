"""
Author:     Matthew Turi (mxt9495@rit.edu)
Course:     IGME-386
Date:       11/19/2020
Assignment: Final Project - Jordan MIH COVID-19 parser
"""

import re
from datetime import datetime

import requests
from bs4 import BeautifulSoup
from flask import Flask, render_template, request

app = Flask(__name__)

ROOT_URL = r"https://corona.moh.gov.jo"
BASE_PATH = r"/en/MediaCenter"


# TODO Implement scheduler for gathering links every 24h
# https://stackoverflow.com/questions/21214270/how-to-schedule-a-function-to-run-every-hour-on-flask

def gather_links():
    """
    Gather all the links to the COVID-19 updates from as many pages as possible. This function will not get links earlier
    than 8/25/2020 because the updates earlier than that were not standardized

    :return: The link to the update pages and a datetime object for the day the update refers to
    """
    all_urls = []
    page_number = 1

    # Keep trying to increment the page number until no results are returned
    while True:
        # Get webpage
        webpage = requests.get("{0}{1}?page={2}".format(ROOT_URL, BASE_PATH, page_number), verify=False)

        # Parse to BS4
        soup = BeautifulSoup(webpage.content, 'html.parser')

        # Find all of the elements that actually contain the links to the COVID updates
        elements = soup.find("div", class_="col-xs-12 innerlist").find("ul").find_all("li")

        # There are no more pages
        if len(elements) == 0:
            break
        else:
            # Generate list of URLs
            for element in elements:
                # Find the link in the element
                link = element.find("a")

                # Check that a link actually exists and the link text is "COVID-19 Updates in Jordan"
                if (link is not None) and ("COVID-19 Updates in Jordan" in link.text):
                    # Parse the element <p> tag into the date string it actually contains
                    date_string = re.sub(r'\s+', ' ', element.find("p").text.split(",")[1]).lstrip().rstrip()
                    date_time_obj = datetime.strptime(date_string, '%d %B %Y')

                    # Break loop if this entry is older than 8/25/2020
                    start_date = datetime(2020, 8, 25)
                    if date_time_obj.date() < start_date.date():
                        break

                    link_path = link["href"]
                    all_urls.append([link_path, date_time_obj])

            page_number += 1

    return all_urls


@app.route('/parse-update')
def parse_update():
    """
    Parses the content of the webpage that contains the information regarding regional cases

    :return: A dict of the region names and their cases count, or None if the update is older than 8/25
    """
    page_id = request.args.get('page_id')
    # Check that this is a page more recent than 8/25, which is when the posting format was standardized
    # 1304 is the page ID number
    if int(page_id) < 1304:
        print("Unsupported update version. Skipping!")
        return None

    # Get webpage
    webpage = requests.get("{0}{1}?page={2}".format(ROOT_URL, BASE_PATH, page_id), verify=False)

    # Parse to BS4
    soup = BeautifulSoup(webpage.content, 'html.parser')
    document_content = soup.find("div", class_="col-xs-12 innertexts").find("p")

    update_dict = {}
    started_content_block = False

    # Iterate through all lines from the content body
    for row in document_content.text.splitlines():
        # Ignore rows up to the first row containing "Internal Cases"
        if "Internal Cases" in row:
            started_content_block = True
            continue
        else:
            if not started_content_block:
                continue

        # Reached the end of the internal cases content block
        if len(row.lstrip().rstrip()) == 0:
            break

        pieces = row[2:].split(" ")
        num_cases = int(pieces[0].replace(",", ""))
        location = pieces[3].replace(",", "").replace(".", "")

        # Handle entries that have additional locality specified in line
        update_dict[location] = num_cases

    return update_dict


@app.route('/data-sources')
def data_sources():
    return render_template('data-sources.html')


@app.route('/')
def index():
    return render_template('index.html')


if __name__ == "__main__":
    # Only for debugging while developing
    app.run(host="0.0.0.0", debug=True, port=5000)

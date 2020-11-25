import re
from datetime import datetime

import requests
from bs4 import BeautifulSoup

ROOT_URL = r"https://corona.moh.gov.jo"
BASE_PATH = r"/en/MediaCenter"


def main():
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

                    link_path = link["href"]
                    all_urls.append([link_path, date_time_obj])

            page_number += 1

    print(all_urls)


if __name__ == '__main__':
    main()

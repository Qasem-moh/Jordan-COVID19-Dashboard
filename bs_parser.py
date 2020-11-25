import re
from datetime import datetime

import requests
from bs4 import BeautifulSoup

ROOT_URL = r"http://corona.moh.gov.jo"
BASE_PATH = r"/en/MediaCenter"


def main():
    # Get webpage
    webpage = requests.get("{0}{1}".format(ROOT_URL, BASE_PATH), verify=False)

    # Parse to BS4
    soup = BeautifulSoup(webpage.content, 'html.parser')

    # Find all of the elements that actually contain the links to the COVID updates
    elements = soup.find("div", class_="col-xs-12 innerlist").find("ul").find_all("li")

    # Generate list of URLs
    all_urls = []
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

    print(all_urls)


if __name__ == '__main__':
    main()

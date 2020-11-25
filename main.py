"""
Author:     Matthew Turi (mxt9495@rit.edu)
Course:     IGME-386
Date:       11/19/2020
Assignment: Final Project - Jordan MIH COVID-19 parser
"""

from flask import Flask

app = Flask(__name__)


@app.route('/')
def index():
    return 'Hello, World!'


if __name__ == "__main__":
    # Only for debugging while developing
    app.run(host="0.0.0.0", debug=True, port=5000)

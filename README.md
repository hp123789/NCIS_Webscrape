# NCIS Webscrape

Scraping data from news article to gather maritime crime data

# Usage

This script uses Python along with supporting tools and libraries to scrape the web for information relating to maritime crimes, which is then organized and compiled into a spreadsheet. A combination of three groups of words are used, in numerous languages, to search the web for relevant news articles. The data is scraped from the news article and double checked with multiple databases to verify and gather additional information based on the original article. The gathered data is then compiled into a spreadsheet for viewing. The intended inputs are a list of search terms and the intended output is a spreadsheet of information about maritime crimes and their specifics.

The packages used are the following:
* Spacy
  * Spacy is used for the majority of the natural language processing (NLP) at this time. It is used to detect entities (names, locations, organizations etc.) from the body of text found in news articles. Spacy provides options to use their preexisting language processing models or the user has the ability to train their own model. The script mostly uses the preexisting models but does use a custom drug entity extraction model as well.
* Beautiful Soup
  * Beautiful Soup is the primary package used to scrape the web. The package is used to collect Google search results as well as retrieving the text from the news articles.
* Selenium
  * Although Beautiful Soup is used for most of the web scraping, Selenium is used when the webpage has a lot of Javascript elements or requires cookies.
* Urllib
  * Urllib is used alongside Beautiful Soup in webscraping.
* Requests
  * Similar to Urllib, Requests is used with Beautiful Soup in webscraping.
* Google Cloud API
  * The Google Cloud API is used only for translation purposes at this time converting any text from English to another language or vice versa.

At the moment, the script searches Google for news articles given a search term and does so in multiple languages. The article text is then extracted and key words are extracted and searched for on a maritime crime database to search for matches. Given a match is found from the keywords, data about the vessel is extracted from the databases, organized, and inputted into a spreadsheet which can be read by a user.

# Installation

Uses Python 3.9

Dependencies can be installed using:
```
$ pip install -r requirements.txt
```

Nothing needs to be modified to run the script and the resulting spreadsheet will be saved in the directory.

# Future Updates



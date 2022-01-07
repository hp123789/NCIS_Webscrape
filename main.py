import itertools
from google.cloud import translate_v2 as translate
import os
import spacy
from urllib.request import Request
import requests
from bs4 import BeautifulSoup
from collections import Counter
import urllib.request
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import pandas as pd
import numpy as np
import datefinder
import re

# Google Cloud API key
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = r"C:/Users/hamza/Downloads/academic-works-331907-8341da4fd674.json"
client = translate.Client()

# Google search headers
headers = {
    "User-Agent":
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3538.102 Safari/537.36 Edge/18.19582"
}

# listing all possible words for search combination
vessel = ['boat', 'vessel', 'craft', 'tanker', 'submarine']
activity = ['drugs', 'narcotics', 'cocaine', 'heroin', 'marijuana', 'pot',
            'hashish', 'poly drugs', 'methamphetamines', 'drug trafficking',
            'narco sub']
action = ['interdicted', 'interdiction', 'caught', 'navy', 'maritime police',
          'coast guard', 'enforcement', 'busted', 'fine', 'sanctioned', 'prison',
          'jail', 'arrested']

# creating search combinations
combinations = list(itertools.product(vessel,activity,action))

#add in sample combination
combinations.insert(0, ['boat', 'heroin', 'arrested'])

#list of languages
languages = ['en', 'fr', 'ar', 'es', 'pt', 'it', 'zh-cn', 'ru', 'id', 'ms', 'sw', 'fa', 'hi']

articles = []

for keywords in combinations:
    for language in languages:
        print(keywords)
        print(language)
        keywords_n = []
        # translating keywords to specified language *not sure if translation is correct
        for word in keywords:
            if language != 'en':
                translation = client.translate(str(word), target_language=language)
                result = (translation["translatedText"])
            else:
                result = word
            keywords_n.append(result)

        result = keywords_n
        print(result)

        # Search query is all three words connected with whitespace
        query = str(result[0] + ' ' + result[1] + ' ' + result[2])
        print(query)


        # State the query, language, and number of results
        params = {
            'q': query,
            'hl': language,
            'num': '3'
        }

        # Searching Google with BeautifulSoup
        html = requests.get('https://www.google.com/search', headers=headers, params=params).text
        soup = BeautifulSoup(html, 'lxml')

        try:
            for result in soup.select('.tF2Cxc'):
                try:
                    title = result.select_one('.DKV0Md').text
                    link = result.select_one('.yuRUbf a')['href']
                    displayed_link = result.select_one('.TbwUpd.NJjxre').text
                    try:
                        snippet = result.select_one('#rso .lyLwlc').text
                    except:
                        snippet = None

                    print(link)

                    articles.append(link)
                except:
                    pass
        except:
            pass

    break

article_body = []

# For each article get the article body *some articles return an error due to cookies
print(len(articles))
i=0
for link in articles:
    print(i)
    try:
        page = requests.get(link)
        soup = BeautifulSoup(page.content, "html.parser")
        print(soup.text)
    #     print('done')
        article_body.append(soup.text)
    except Exception as e:
        print(e)
    i+=1


translated_articles = []

# Translate the article body to English
for article in article_body:
    try:
        translation = client.translate(str(article), target_language="en")
        result = (translation["translatedText"])
    except Exception as e:
        result = article
        print(e.message)
    translated_articles.append(result)

nlp = spacy.load('en_core_web_lg')

# Using NLP to find dates in the article body
def find_dates(text):
    dates = []
    matches = datefinder.find_dates(text)
    for match in matches:
        dates.append(match.strftime('%m/%d/%Y'))
    return dates

# Initializing the Excel sheet
NCIS_sheet = pd.DataFrame(
        columns=['Name of Vessel', 'Vessel Type', 'Flag', 'Name of Company', 'Exact Location', 'EEZ',
                 'Date of Interdiction', 'Nature of Goods', 'Agency', 'Pictures', 'Fine'])

# Fleetmon information search
for article in translated_articles:
    boat_info = []
    boat_info2 = []

    # Find the 7 most commonly recurring names in the article
    doc = nlp(article)
    words = [i for i in doc.ents if i.label_ == 'PERSON']
    keywords = [word for word, word_count in Counter(words).most_common(7)]

    print(keywords)

    # For each name it searches Fleetmon to see if there is a result
    for name in keywords:
        # gets terms extracted from previous article
        search_term = str(name)
        search_term = re.sub(r'([^\s\w]|_)+', '', search_term)
        search_term = search_term.replace(" ", "+")
        print(search_term)

        try:
            # searches fleetmon for related articles
            parser = 'html.parser'
            resp = urllib.request.urlopen("https://www.fleetmon.com/maritime-news/search/?q=" + search_term)
            soup = BeautifulSoup(resp, parser, from_encoding=resp.info().get_param('charset'))

            articles = []

            for link in soup.find_all('a', href=True):
                if link['href'].startswith('/maritime-news/20'):
                    articles.append('https://www.fleetmon.com' + link['href'])

            #     print(articles)
        except:
            print('error: fleetmon')

        # If an article is found, it searches for the boat name in the article
        try:
            url = articles[0]
            options = Options()
            options.add_argument("--headless")
            driver = webdriver.Chrome(options=options)
            driver.get(url)
            stages = driver.find_elements(By.CLASS_NAME, "vessel-link")
            vessel_info = stages[0].get_attribute('href')

            # Also retrieving the boat picture
            picture_ref = driver.find_elements(By.CLASS_NAME, "margin-t-5")
            picture_ref = picture_ref[0].get_attribute("data-src")
            print(picture_ref)

            vessel_image = '<img src = "' + picture_ref + '"/>'

            #         print(vessel_info)

            driver.close()

            # Retrieving the vessel info which is organized below
            page = requests.get(vessel_info)

            soup = BeautifulSoup(page.content, "html.parser")

            data = soup.find_all("div", class_="col-lg-6")

            # for i in data:
            #     print(i.prettify(), end="\n"*2)

            #         print('-----------------------------------------')

            # Organizing the boat info into its respective categories
            boat_info = [item.get_text(strip=True) for item in soup.select("span.font-daxmedium")]
            boat_info = boat_info[2:14]
            boat_info.append(vessel_image)
            #         print(boat_info)
            categories = ['AIS Name', 'Type', 'Flag', 'IMO', 'MMSI', 'Callsign', 'Year Built', 'Length', 'Width',
                          'Draught', 'Speed', 'Gross Tonnage', 'Image']
            boat_info2 = list(zip(categories, boat_info))
            print(boat_info2)
            break
        except:
            print('no results')


    name = np.NaN
    vessel = np.NaN
    flag = np.NaN
    company = np.NaN
    location = np.NaN
    eez = np.NaN
    date = np.NaN
    drug = np.NaN
    org = np.NaN
    pictures = np.NaN
    fine = np.NaN

    # Using NLP to retrieve the date
    try:
        date = find_dates(article)[0]
        print(date)
    except:
        pass

    # Using NLP to retrieve the drug
    try:
        nlp = spacy.load('drug_ner')
        doc = nlp(article)
        drug = [(X.text, X.label_) for X in doc.ents][0][0]
        print(drug)
    except:
        pass

    # Using NLP to retrieve the organization
    try:
        nlp = spacy.load('en_core_web_lg')
        doc = nlp(article)
        for ent in doc.ents:
            if ent.label_ == "ORG":
                org = ent
                print(org)
                break
    except:
        pass


    # Using NLP to retrieve the money amount
    def money_nlp(doc):
        with doc.retokenize() as retokenizer:
            for money in [e for e in doc.ents if e.label_ == 'MONEY']:
                if doc[money.start - 1].is_currency:
                    retokenizer.merge(doc[
                                      money.start - 1:money.end])

        return doc

    nlp.add_pipe(money_nlp, after='ner')

    try:
        for ent in doc.ents:
            if ent.label_ == "MONEY":
                fine = ent
                print(fine)
                break
    except:
        pass

    # Adding all the information to the Dataframe
    try:
        name = boat_info[0]
    except:
        pass
    try:
        vessel = boat_info[1]
    except:
        pass
    try:
        flag = boat_info[2]
    except:
        pass
    company = company
    location = location
    eez = eez
    date = date
    goods = drug
    agency = org
    try:
        pictures = boat_info[12]
    except:
        pictures = pictures
    fine = fine

    information = pd.Series([name, vessel, flag, company, location, eez, date, goods, agency, pictures, fine],
                            index=NCIS_sheet.columns)
    NCIS_sheet = NCIS_sheet.append(information, ignore_index=True)
    NCIS_sheet.to_html(escape=False)
    print(NCIS_sheet)

# Writing the Dataframe to an Excel sheet and saving it locally
# display(HTML(NCIS_sheet))
NCIS_sheet.to_excel("NCIS_GroupA.xlsx")
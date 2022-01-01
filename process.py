from finbert import finbert
from transformers import AutoModelForSequenceClassification
import argparse
import re
import os
import json
import json2html
import string
from bs4 import BeautifulSoup
from requests_html import HTMLSession

printable = set(string.printable)
base_url = "https://www.moneycontrol.com/news/business/stocks"
valid_url = "https://www.moneycontrol.com/news/business/markets"
    
def get_links(soup):
    stocknews = set()
    otherlinks = set()
    
    for link in soup.find_all('a'):
        childLink = link.get('href',None)

        if childLink is not None and 'mailto:' not in childLink and 'Download' not in childLink:
            childLink = childLink.rstrip("/")
            if childLink.startswith(base_url) or childLink.startswith(valid_url):
                if childLink not in stocknews:
                    stocknews.add(childLink)
            elif childLink not in otherlinks:
                otherlinks.add(childLink)
    return stocknews, otherlinks

def get_html(session, url):
    page = {}
    
    try:
        resp = session.get(url)
        soup = BeautifulSoup(resp.html.html, 'html.parser')
        page['title'] = soup.title.string
        stocknews, others = get_links(soup)
        page["stock-links"] = list(stocknews)
        page["other-links"] = list(others)
        page['text'] = soup.get_text()
    except Exception as e:
        print("cannot scrap", url, e)
        
    return page

def get_levels(session, url, num, summary):
    page = get_html(session, url)
    summary[url] = page
    print(num, url)
    if num <= 1:
        return
    
    for child_url in page['stock-links']:
        if child_url not in summary:
            get_levels(session, child_url, num - 1, summary)

def process(levels, output):
    session = HTMLSession()
    summary = {}
    get_levels(session, base_url, levels, summary)
    with open(output + ".json", "w") as out_file:
        json.dump(summary, out_file) 
        print("Raw output written to output" + ".json")
    
    model = AutoModelForSequenceClassification.from_pretrained('./model', num_labels=3, cache_dir=None)
    
    sentiments = []
    
    for url in summary.keys():
        if url == base_url or url == valid_url:
            continue
        
        page = summary[url]
        print("computing sentiment of page: ", url) 
        s = ''.join(filter(lambda x: x in printable, page['text']))
        s = s.replace(".", ";")
        
        sentiment = {'url': url}
        sentiment['sentiment'] = finbert.predict(s, model)['prediction'].values[0]
        sentiments.append(sentiment)
    
    sentimentJson = json.dumps(sentiments)
    htmlOutput = json2html.convert(json = sentimentJson)
    with open(output + ".html", "w") as out_file:
        print(htmlOutput, out_file)

    print("Summary information generated in ", output + ".html")
    
    
parser = argparse.ArgumentParser(description='Sentiment analyzer')
parser.add_argument('--levels', type=int, help='Number of nested links to scrap', required=True)
parser.add_argument('--output', type=str, help='output name', required=True)
args = parser.parse_args()

if args.levels < 1:
    print("Please choose level >=1")
else:
    process(args.levels + 1, args.output)

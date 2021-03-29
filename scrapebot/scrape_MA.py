import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime, date
import pandas

# Year Month Day
# min_date = '2021-03-10' #datetime(2021, 3, 10, 0, 0)

def scrapeMA(min_date):
    URL = 'https://www.mass.gov/lists/press-releases-related-to-covid-19'
    page = requests.get(URL)

    soup = BeautifulSoup(page.content, 'html.parser')
    news_sections = soup.find_all('div', {'class': 'ma__download-link'})
    return generate_content(news_sections, min_date)

def generate_content(news_sections, min_date):
    content = []
    for news in news_sections:
        news_date = get_news_date(news)
        if(news_date >= datetime.strptime(min_date, '%Y-%m-%d')):
            content += [(news_date.strftime('%Y-%m-%d'), get_news_title(news), get_news_link(news))] 
    
    return content


def get_news_date(news):
    date_p = news.find('p')
    match = re.search(r'(\d+/\d+/\d+)', date_p.contents[0])
    news_date = pandas.to_datetime(match.group(), format = '%m/%d/%Y', infer_datetime_format=True)
    return news_date.to_pydatetime()

def get_news_title(news):
    news_content = news.find('a')
    return news_content.contents[0]

def get_news_link(news):
    news_link = news.find('a')['href']
    return news_link

#print(scrapeMA("2021-03-10"))
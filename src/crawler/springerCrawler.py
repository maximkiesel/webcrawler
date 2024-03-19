from elasticsearch.helpers import bulk
from selenium import webdriver
import time
import math
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from elasticsearch import Elasticsearch
import src.topicModeling.topicModelar as tm
import re

def run(search_term="computer science", page_limit=10, db=True):
    if db:
        # connection to elasticsearch
        es = Elasticsearch(['http://localhost:9200'])


    i = 1
    page_num = 1
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    driver = webdriver.Chrome(chrome_options, Service(ChromeDriverManager().install()))

    print("crawler start")

    # ACM digital library URL and the search_term which is searched for
    driver.get("https://link.springer.com/search?new-search=true&query=" + search_term + "&content-type=Article&sortBy=relevance&page=" + str(page_num))
    print("crawler: " + driver.title)

    # wait for page to load
    time.sleep(1)

    # finding out how many pages in total we can crawl
    num_of_articles_string = driver.find_element(By.XPATH, "/html/body/div[4]/div/div[3]/div/div[1]/div/div[2]/div/div[1]").text
    numbers = re.findall(r'[\d,]+', num_of_articles_string)
    num_of_articles = int(numbers[-1].replace(',', ''))

    elements_per_page = 50
    #springer only allows 50 pages
    max_page_num = min(math.ceil(int(num_of_articles) / elements_per_page), page_limit)

    print("search term = " + search_term)
    print("Total crawled pages = ", max_page_num)
    print("Total articles that are crawled = " + str(max_page_num * elements_per_page))

    print("---------------------------------------------------------------------------------------------------")

    ######################################################### CRAWLER PART ###############################################################

    for j in range(1, max_page_num + 1):
        driver.get("https://link.springer.com/search?new-search=true&query=" + search_term + "&content-type=Article&sortBy=relevance&page=" + str(page_num))

        articles = driver.find_elements(By.CLASS_NAME, "c-card-open")

        for article in articles:
            start_time = time.perf_counter()
            # crawling the title of each article in each page
            try:
                # Get Title
                title = driver.find_element(By.XPATH, '/html/body/div[4]/div/div[3]/div/div[2]/div[2]/ol/li[' + str(i) + ']/div/div/h3/a')
                title_text = title.text
                print(title_text)
                driver.execute_script("arguments[0].click();", title)
                time.sleep(1)

                # Get abstract
                abstract_text = driver.find_element(By.ID, 'Abs1-content').find_element(By.TAG_NAME, "p").text
                print(abstract_text)

                # Get date
                date_text = driver.find_element(By.XPATH, '//*[@id="article-info-content"]/div/div[2]/ul/li[3]/p/span[2]/time')
                date_text = date_text.text

                # get authors
                author_elements = driver.find_elements(By.CLASS_NAME, "c-article-author-list__item")
                authors_names = ""
                for author in author_elements:
                    inner_span = author.find_element(By.CSS_SELECTOR, "a")
                    authors_names = authors_names + ", " + inner_span.text
                authors_names = authors_names[2:]

                # get link to article
                link_text = driver.find_element(By.XPATH, '//abbr[@title="Digital Object Identifier"]/following-sibling::span[2]').text

            except:
                i = i + 1
                print("skipped: could not get abstract")
                driver.back()
                continue

            # topic modeling
            topics = tm.model_topics(title_text, abstract_text);

            # making a dictionary out of the crawled data
            temp = {'Title': title_text,
                    'date': date_text,
                    'authors': authors_names,
                    'link': link_text,
                    'abstract': abstract_text,
                    'topics': topics}

            print(temp)
            if db:
                # inserting article into elasticsearch db, id = doi
                es.index(index='article', id=link_text, body=temp)

            keywords = []

            for topic in topics:
                for keyword in topic['topic']:
                    keywords.append({'keyword': keyword["keyword"]})

            actions = [
                {
                    "_index": "keyword",
                    "_id": name['keyword'],
                    "_source": name
                }
                for name in keywords
            ]

            if db:
                # inserting topic names to elasticsearch seperatly
                bulk(es, actions)


            # going back to main page
            driver.back()

            print("Page number = ", page_num)
            print("Total number of articles in this page: ", len(articles))
            print("Scraping article # ", i)
            end_time = time.perf_counter()
            print(f"Execution time: {end_time - start_time} seconds")
            print("---------------------------------------------------------------------------------------------------")
            if i <= len(articles):
                i = i + 1  # going to the next article
            else:
                break

        i = 1
        page_num = page_num + 1  # going to the next page

if __name__ == '__main__':
    run("computer science", 10, True)
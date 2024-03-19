from elasticsearch.helpers import bulk
from selenium import webdriver
import math
import time
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from elasticsearch import Elasticsearch
import src.topicModeling.topicModelar as tm


def run(search_term="computer science", page_limit=10, db=True):
    if db:
        # connection to elasticsearch
        es = Elasticsearch(['http://localhost:9200'])

    i = 1
    page_num = 0
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    driver = webdriver.Chrome(chrome_options, Service(ChromeDriverManager().install()))

    print("crawler start")

    # ACM digital library URL and the keyword which is searched for
    driver.get("https://dl.acm.org/action/doSearch?fillQuickSearch=false&ContentItemType=research-article&expand=dl&AllField=Keyword%3A%28" + search_term + "%29+AND+Abstract%3A%28" + search_term + "%29&pageSize=50&startPage=" + str(page_num) + "&AvailableFormat=lit%3Apdf")

    time.sleep(1)

    # finding out how many pages in total we can crawl
    num_of_articles = driver.find_element(By.CLASS_NAME, "hitsLength").text
    num_of_articles = num_of_articles.replace(',', '')

    elements_per_page = 50
    # set max page limit to 50 or less
    max_page_num = min(math.ceil(int(num_of_articles) / elements_per_page), page_limit)

    print("ACM Digital Library")
    print("search term = " + search_term)
    print("Total crawled pages = ", max_page_num)
    print("Total articles that are crawled = " + str(max_page_num * elements_per_page))

    print("---------------------------------------------------------------------------------------------------")

    ######################################################### CRAWLER PART ###############################################################

    for j in range(1, max_page_num + 1):
        driver.get(
            "https://dl.acm.org/action/doSearch?fillQuickSearch=false&ContentItemType=research-article&expand=dl&AllField=Keyword%3A%28"
            + search_term + "%29+AND+Abstract%3A%28" + search_term + "%29&pageSize=50&startPage=" + str(
                page_num) + "&AvailableFormat=lit%3Apdf")

        articles = driver.find_elements(By.CLASS_NAME, "issue-item__content-right")
        for article in articles:
            start_time = time.perf_counter()

            try:
                # Get Title
                title = driver.find_element(By.XPATH, '//*[@id="skip-to-main-content"]/main/div[1]/div/div[2]/div/ul/li[' + str(i) + ']/div[2]/div[2]/div/h5/span/a')
                title_text = title.text
                driver.execute_script("arguments[0].click();", title)
                time.sleep(1)

                # Get Abstract
                abstract = driver.find_element(By.XPATH, '//*[@id="skip-to-main-content"]/main/div[1]/article/div[2]/div[2]/div[2]/div[1]/div/div[2]')  # CSS tag of the abstract
                p_elements = abstract.find_elements(By.XPATH, ".//p")
                for p in p_elements:
                    abstract_text = abstract.text + p.text

                if abstract_text == '':
                    raise Exception("no abstract found")

                # Get date
                date = driver.find_element(By.XPATH, '//*[@id="skip-to-main-content"]/main/div[1]/article/div[1]/div[2]/div/div/div[5]/span[2]')
                date_text = date.text

                # Get Authors
                author_elements = driver.find_elements(By.CLASS_NAME, "loa__author-name")
                authors_names = ""
                for author in author_elements:
                    inner_span = author.find_element(By.CSS_SELECTOR, "span > span")
                    authors_names = authors_names + ", " + inner_span.text
                authors_names = authors_names[2:]

                # Get DOI Link
                link_text = driver.find_element(By.CLASS_NAME, 'issue-item__doi').text

            # If Failed to retrieve some Data, skip whole article
            except:
                i = i + 1
                print("skipped: could not get data from article")
                print("---------------------------------------------------------------------------------------------------")
                driver.back()
                continue

            # topic modeling
            topics = tm.model_topics(title_text, abstract_text)
            tm.test_coherence(title_text + abstract_text)

            # making a dictionary out of the crawled data
            temp = {'Title': title_text,
                    'date': date_text,
                    'authors': authors_names,
                    'link': link_text,
                    'abstract': abstract_text,
                    'topics': topics}

            print(temp)
            if db:
                # inserting article into elasticsearch db
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

            driver.back()
            print("Scraping article # ", i)
            print("Total article number # ", i * j)
            print("Page number = ", page_num + 1)
            print("Total number of articles in this page: ", len(articles))
            print("article scraped: " + str(temp))
            end_time = time.perf_counter()
            print(f"Execution time: {end_time - start_time} seconds")
            print("---------------------------------------------------------------------------------------------------")
            if i <= len(articles):
                i = i + 1  # going to the next article
            else:
                break

        i = 1
        page_num = page_num + 1  # going to the next page in ACM digital library

if __name__ == '__main__':
    run("computer science", 10, False)
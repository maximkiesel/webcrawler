import unittest
from io import StringIO
import ast

from selenium.common import NoSuchElementException

import src.crawler.acmCrawler
from unittest.mock import patch, MagicMock
import sys


class TestMyCrawler(unittest.TestCase):
    @patch('src.crawler.acmCrawler.webdriver.Chrome')
    def test_runSuccess(self, mock_chrome):
        sys.stdout = StringIO()

        totalArticleNumber = "1"
        title = "test title"
        date = "01.01.2011"
        link = "https://test.test"
        abstractText = "test abstract"
        author = "Maximilian Mustermann"

        mock_driver = MagicMock()
        article_mock = MagicMock(text=totalArticleNumber)
        title_mock = MagicMock(text=title)
        abstract_mock = MagicMock(text="")
        date_mock = MagicMock(text=date)
        link_mock = MagicMock(text=link)
        mock_p_elements = [MagicMock(text=abstractText)]
        # mock of find_element
        mock_driver.find_element.side_effect = [
            article_mock,   # article mock
            title_mock,     # title mock
            abstract_mock,  # abstract mock
            date_mock,      # date mock
            link_mock,      # link mock
        ]
        # Get Abstract mock
        abstract_mock.find_elements.return_value = mock_p_elements
        # Get Articles mock
        articles_mock = [MagicMock(text='article element 1')]
        # Get authors mock
        inner_mock = MagicMock(text='inner Element')
        author_elements_mock = [inner_mock]
        # mock of find_elements
        mock_driver.find_elements.side_effect = [
            articles_mock,  # get abstracts mock
            author_elements_mock,  # get authors mock
        ]
        # Get author mock
        authors_mock = MagicMock(text=author)
        inner_mock.find_element.return_value = authors_mock
        # Get Chrome Driver Mock
        mock_chrome.return_value = mock_driver

        # start acmCrawler
        src.crawler.acmCrawler.run("computer science", 1, False)
        # Get console output
        output = sys.stdout.getvalue()
        lines = output.split('\n')
        # Get article from console output
        article_dict = {}
        for line in lines:
            if line.startswith('article scraped:'):
                temp = line.replace("article scraped:", "").strip()
                article_dict = ast.literal_eval(temp)
                break
        # assert that the date is the same
        self.assertEqual(article_dict["Title"], title)
        self.assertEqual(article_dict["date"], date)
        self.assertEqual(article_dict["authors"], author)
        self.assertEqual(article_dict["link"], link)
        self.assertEqual(article_dict["abstract"], abstractText)

    @patch('src.crawler.acmCrawler.webdriver.Chrome')
    def test_run_noAbstract(self, mock_chrome):
        sys.stdout = StringIO()

        totalArticleNumber = "1"
        title = "test title"
        date = "01.01.2011"
        link = "https://test.test"
        abstractText = "test abstract"
        author = "Maximilian Mustermann"

        mock_driver = MagicMock()
        article_mock = MagicMock(text=totalArticleNumber)
        title_mock = MagicMock(text=title)
        abstract_mock = MagicMock(text="")
        date_mock = MagicMock(text=date)
        link_mock = MagicMock(text=link)

        mock_driver.find_element.side_effect = [
            article_mock,   # article call
            title_mock,     # title call
            NoSuchElementException("Element nicht gefunden"),  # abstract call
            date_mock,      # date call
            link_mock,      # link call
        ]

        mock_p_elements = [MagicMock(text=abstractText)]
        abstract_mock.find_elements.return_value = mock_p_elements;

        inner_mock = MagicMock(text='element 2')

        mock_elements_1 = [MagicMock(text='element 1')]
        mock_elements_2 = [inner_mock]

        mock_driver.find_elements.side_effect = [
            mock_elements_1,  # first mock of find_elements
            mock_elements_2,  # second
        ]

        authors_mock = MagicMock(text=author)

        inner_mock.find_element.return_value = authors_mock

        mock_chrome.return_value = mock_driver

        # method call
        src.crawler.acmCrawler.run("computer science", 1, False)

        output = sys.stdout.getvalue()
        lines = output.split('\n')

        temp = ""
        for line in lines:
            if line.startswith('skipped:'):
                temp = line
                break

        self.assertEqual("skipped: could not get data from article", temp)


if __name__ == '__main__':
    unittest.main()

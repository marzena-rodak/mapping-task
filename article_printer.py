import requests
import json
from models import Article
from datetime import datetime
from html.parser import HTMLParser
import schedule
import time

#parser that will be used further for cleaning the data out of html tags
class html_parser(HTMLParser):
    text = ''
    def handle_data(self,data):
        self.text += data


class ArticlePrinter:
    base_url = 'https://mapping-test.fra1.digitaloceanspaces.com/data/'
    articles_id_list = []
    article_parser = html_parser()

    #function that renames keys in dictionary so that they match requried names from classes imported from models
    def format_date_field(self, my_dict):
        try:
            my_dict['publication_date'] = my_dict.pop('pub_date')
            my_dict['publication_date'] = datetime.fromisoformat(my_dict['publication_date'].replace(';',':'))
        except:
            pass
        try:
            my_dict['modification_date'] = my_dict.pop('mod_date')
            my_dict['modification_date'] = datetime.fromisoformat(my_dict['modification_date'].replace(';',':'))
        except:
            pass


    def get_article(self, article_id):
        url = f'{self.base_url}articles/{article_id}.json'
        response_article = requests.get(url)
        article_details = json.loads(response_article.text)

        self.format_date_field(article_details)
        article_details['url'] = url

        if any('media' in d.values() for d in article_details['sections']):
            media_url = f'{self.base_url}media/{article_id}.json'
            response_media = requests.get(media_url)
            media_details = json.loads(response_media.text)

        for elem in article_details['sections']:
            if elem['type'] == 'text':
                self.article_parser.text = ''
                self.article_parser.feed(elem['text'])
                elem['text'] = self.article_parser.text
            elif elem['type'] == 'media':
                media_dict = [i for i in media_details if i['id'] == elem['id']]
                self.format_date_field(media_dict[0])
                for i in media_dict[0].keys():
                    elem[i] = media_dict[0][i]
                
        try:
            article_details['categories'] = article_details.pop('category')
            cat = article_details['categories']
            article_details['categories'] = cat if type(cat)==list else [cat]
        except:
            pass

        return Article(**article_details)


    def my_fun(self):
        try:
            response = requests.get(f'{self.base_url}list.json')
            response.raise_for_status()
        except requests.exceptions.HTTPError as err:
            print(err)
        else:

            articles_list= json.loads(response.text)
            newest_articles_list = [art for art in articles_list if art['id'] not in self.articles_id_list]

            for article in newest_articles_list:
                article_id = article['id']
                #add article id to list so it wont be repulled next time script runs
                self.articles_id_list += [article_id]
                try:
                    article_k = self.get_article(article_id)
                    print(article_k)
                except Exception as e:
                    print(f"Downloading article {article_id} failed.")
                    print(f"Error: {e}")


    def run(self, interval=5):
        schedule.every(interval).minutes.do(self.my_fun)
        while True:
            schedule.run_pending()
            time.sleep(1)

# THIS IS BOT IS STILL RUNNING!!!! FOLLOW ME ON TWITTER: @NEWSABOUTBTC

import coinlib
import News
import shelve
import time
import twython
import datetime
import random


class TwitterBot():

    def __init__(self):
        self.controller = twython.Twython(
            'YOUR_TWITTER_TOKENS_HERE',
            )
        self.news_controller = News.News()
        print('>>> ({}) Bot started.'.format(self.get_time()))

    def get_last_posts(self):
        with shelve.open('posts') as posts_db:
            last_posts = []
            for portal_id in posts_db:
                if portal_id != 'next_btc_price':
                    last_posts.append(posts_db[portal_id])
        return last_posts

    def pull_last_news(self):
        self.news_controller.refresh()
        return {
            'coindesk': self.news_controller.coindesk[0],
            'cointelegraph': self.news_controller.cointelegraph[0],
            'cryptocurrencynews': self.news_controller.cryptocurrencynews[0],
            'ccn': self.news_controller.ccn[0],
            'newsbtc': self.news_controller.newsbtc[0]
            }

    def format_to_post(self, news):
        title = news['title']
        link = news['link']
        tags = ''
        for tag in news['tags']:
            tag = tag.lower()
            if len(tag.split()) == 1:
                for word in title.lower().split():
                    if tag == word or word.startswith(tag):
                        tag_position = title.lower().find(tag)
                        title = title[:tag_position]+'#'+title[tag_position:]
                        break
                else:
                    if tag.startswith('#'):
                        tag = tag[1:]
                    tags += '#{} '.format(tag)
        if len(tags) >= 1:
            return '{}\n\n{}\n{}'.format(title, tags, link)
        return '{}\n\n{}'.format(title, link)

    def post_news(self, portal_id, status):
        print('-'*15)
        print('>>> ({}) Preparing to post:\n{}'.format(self.get_time(),
                                                       status))
        # Checks whether status has been already posted or not
        if status in self.get_last_posts():
            print('>>> ({}) Status has been already posted.'.format(
                self.get_time()))
            return
        # Posts if not
        try:
            self.controller.update_status(status=status)
            print('>>> ({}) Status has been '.format(self.get_time())
                  + 'posted successfully.')
        except Exception as err:
            print('>>> ({}) Error posting status: '.format(self.get_time())
                  + '{}'.format(err))
        # Adds status to posts database
        with shelve.open('posts') as posts_db:
            posts_db[portal_id] = status
            print('>>> ({}) Status saved to database.'.format(self.get_time()))
        # Sleeps for next post
        print('>>> ({}) Sleeping for 30 seconds.'.format(self.get_time()))
        for n in range(30):
            time.sleep(1)

    def post_btc_price(self):
        print('-'*15)
        print('>>> ({}) Preparing to post Bitcoin price.'.format(
            self.get_time()))
        now = datetime.datetime.now()
        # Checks if it's time to post
        with shelve.open('posts') as posts_db:
            time = posts_db['next_btc_price']
            if now < time:
                print('>>> Not yet. Time is: {}.'.format(time))
                return
            # Defines new time to post if yes
            new_time = now+datetime.timedelta(
                hours=random.randint(3, 12))
            posts_db['next_btc_price'] = new_time
            print('>>> ({}) Defined new Bitcoin price time: '.format(
                self.get_time())
                  + '{}.'.format(new_time))
        # Collects status if yes
        status = self.prepare_btc_price()
        # Posts
        try:
            self.controller.update_status(status=status)
            print('>>> ({}) Status has been '.format(self.get_time())
                  + 'posted successfully.')
        except Exception as err:
            print('>>> ({}) Error posting status: '.format(self.get_time())
                  + '{}'.format(err))

    def prepare_btc_price(self):
        bitcoin = coinlib.get_coins('btc')
        btc_price = bitcoin['btc']['price']
        variation = bitcoin['btc']['percent_change_24h']
        return '1 #Bitcoin = US$ {:,.2f} ({:.2f}%)'.format(btc_price,
                                                           variation)

    def get_time(self):
        time_in_epoch = time.time()
        time_in_datetime = datetime.datetime.fromtimestamp(time_in_epoch)
        return time_in_datetime

    def start(self):
        while True:
            print('>>> ({}) Pulling news for updates.'.format(self.get_time()))
            news = self.pull_last_news()
            for news_portal in news:
                status = self.format_to_post(news[news_portal])
                self.post_news(portal_id=news_portal, status=status)
            self.post_btc_price()
            print('>>> ({}) Sleeping for 1 minute.'.format(self.get_time()))
            time.sleep(60)


TwitterBot().start()

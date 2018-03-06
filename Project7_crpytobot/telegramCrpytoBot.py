import telegram, telegram.ext
import feedparser, ssl
import shelve
import logging
import csv
import praw
from requests import get as rget
from json import loads
from emoji import emojize
from random import randint

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

u = telegram.ext.Updater(token='YOUR_TELEGRAM_TOKEN_HERE')
d = u.dispatcher
j = u.job_queue

reddit = praw.Reddit(client_id='YOUR_REDDIT_CLIENT_ID_HERE',
                     client_secret='YOUR_REDDIT_CLIENTE_SECRET_HERE',
                     user_agent='YOUR_REDDIT_USER_AGENT_HERE'
                     )

if hasattr(ssl, '_create_unverified_context'):
    ssl._create_default_https_context = ssl._create_unverified_context

def new_user(incoming_update):
    update_info = incoming_update.message
    chat_id     = str(update_info['chat']['id'])
    f_name      = update_info['chat']['first_name']
    l_name      = update_info['chat']['last_name']
    date        = update_info['date']
    users_db    = shelve.open('users')
    if chat_id not in list(users_db.keys()):
        users_db[chat_id] = {
            'date'      : date   ,
            'f_name'    : f_name ,
            'l_name'    : l_name ,
            'auto_news' : True   ,
            'portfolio' : {}
            }
    users_db.close()

def get_coins():
    raw_data = rget('https://api.coinmarketcap.com/v1/ticker/?limit=0').text
    parsed_data = loads(raw_data)
    final_data = {}
    for coin in parsed_data:
        final_data[coin['symbol']] = coin
    return final_data

def get_coin_by_id(coin_id):
    raw_data = rget(f'https://api.coinmarketcap.com/v1/ticker/{coin_id}/').text
    parsed_data = loads(raw_data)
    if isinstance(parsed_data, list):
        return parsed_data[0]
    return parsed_data

def get_global_data():
    raw_data = rget('https://api.coinmarketcap.com/v1/global/').text
    parsed_data = loads(raw_data)
    return parsed_data

def get_news(news_portal='cd'):
    news_links = {
        'cd'  : 'http://feeds.feedburner.com/Coindesk?format=xml' ,
        'ct'  : 'https://cointelegraph.com/feed'                  ,
        'ccn' : 'https://www.ccn.com/feed/'
        }
    parsed_data = feedparser.parse(news_links[news_portal])
    return parsed_data['items']

def start_message(bot, update):
    bot.send_chat_action(chat_id=update.message.chat_id, action=telegram.ChatAction.TYPING)
    f_name = bot.get_chat(update.message.chat_id)['first_name']
    f_name = '' if not f_name else f', {f_name}'
    wave_emoji = emojize(':wave:', use_aliases=True)
    message = f'''Hey there{f_name}! {wave_emoji}

I'm CrpytoBot, your personal crypto-specialist.

If you want a quick rundown of my skills, simply type "/" below. For further assistance, use /help.

Why don't you start by typing _/price bitcoin_ below?'''
    new_user(update)
    bot.send_message(chat_id=update.message.chat_id,
                     text=message,
                     parse_mode=telegram.ParseMode.MARKDOWN)
    new_feature(bot, update, True, [f_name])

def new_feature(bot, update, to_run, addtl_data):
    if not to_run:
        return
    f_name = f_name = bot.get_chat(update.message.chat_id)['first_name']
    f_name = 'W' if not f_name else f'{f_name}, w'
    message = f'{f_name}e need *jokes*!\nSend yours with /sendjoke.'
    bot.send_message(chat_id=update.message.chat_id,
             text=message,
             parse_mode=telegram.ParseMode.MARKDOWN)
    
def get_price_by_command(bot, update, args):
    bot.send_chat_action(chat_id=update.message.chat_id, action=telegram.ChatAction.TYPING)
    coins = get_coins()
    price_in_text = ''
    if len(args) == 0:
        f_name = bot.get_chat(update.message.chat_id)['first_name']
        f_name = '' if not f_name else f', {f_name}'
        messages = [
            f'Hey{f_name}! '+emojize(':wave:', use_aliases=True) ,
            'It seems like you were trying to retrieve some prices, is that correct?' ,
            'Well, I think you forgot to tell me for which coins you want them... But don\'t worry—let\'s figure it out!' ,
            'Try typing...' ,
            '_/price bitcoin_' ,
            'or maybe...' ,
            '_/price btc ltc ethereum_'
            ]
        bot.send_message(chat_id=update.message.chat_id, text=messages[0], parse_mode=telegram.ParseMode.MARKDOWN)
        for message in messages[1:-1]:
            bot.send_message(chat_id=update.message.chat_id, text=message, parse_mode=telegram.ParseMode.MARKDOWN, disable_notification=True)
        bot.send_message(chat_id=update.message.chat_id, text=messages[-1], parse_mode=telegram.ParseMode.MARKDOWN, disable_notification=True, reply_markup=telegram.ForceReply())
        return
    not_found = False
    for arg in args:
        arg = arg.upper()
        if arg not in coins:
            coin = get_coin_by_id(arg)
            if 'id' in coin:
                name   = coin['name']
                symbol = coin['symbol']
                price  = round(float(coin['price_usd']), 2)
                var    = coin['percent_change_24h']
            else:
                price_in_text += f'• _{arg}_ not found\n'
                not_found = True
                continue
        else:
            name   = coins[arg]['name']
            symbol = coins[arg]['symbol']
            price  = round(float(coins[arg]['price_usd']), 2)
            var    = coins[arg]['percent_change_24h']
        price_in_text += f'• *{name}* (_{symbol}_): US$ {price:,.2f} ({var}%)\n'
    if len(args) == 1:
        price_in_text = price_in_text[2:]
        if not not_found:
            price_in_text = '> Showing _price in USD_\n'+price_in_text
    else:
        price_in_text = '> Showing _prices in USD_\n'+price_in_text
    bot.send_message(chat_id=update.message.chat_id, text=price_in_text, parse_mode=telegram.ParseMode.MARKDOWN)

def get_price_btc_by_command(bot, update, args):
    bot.send_chat_action(chat_id=update.message.chat_id, action=telegram.ChatAction.TYPING)
    coins = get_coins()
    price_in_text = ''
    if len(args) == 0:
        f_name = bot.get_chat(update.message.chat_id)['first_name']
        f_name = '' if not f_name else f', {f_name}'
        messages = [
            f'Hey{f_name}! '+emojize(':wave:', use_aliases=True) ,
            'It seems like you were trying to retrieve some prices, is that correct?' ,
            'Well, I think you forgot to tell me for which coins you want them... But don\'t worry—let\'s figure it out!' ,
            'Try typing...' ,
            '_/pricebtc bitcoin_' ,
            'or maybe...' ,
            '_/pricebtc ltc eth ripple_'
            ]
        bot.send_message(chat_id=update.message.chat_id, text=messages[0], parse_mode=telegram.ParseMode.MARKDOWN)
        for message in messages[1:-1]:
            bot.send_message(chat_id=update.message.chat_id, text=message, parse_mode=telegram.ParseMode.MARKDOWN, disable_notification=True)
        bot.send_message(chat_id=update.message.chat_id, text=messages[-1], parse_mode=telegram.ParseMode.MARKDOWN, disable_notification=True, reply_markup=telegram.ForceReply())
        return
    not_found = False
    for arg in args:
        arg = arg.upper()
        if arg not in coins:
            coin = get_coin_by_id(arg)
            if 'id' in coin:
                name   = coin['name']
                symbol = coin['symbol']
                price  = coin['price_btc']
            else:
                price_in_text += f'• _{arg}_ not found\n'
                not_found = True
                continue
        else:
            name   = coins[arg]['name']
            symbol = coins[arg]['symbol']
            price  = coins[arg]['price_btc']
        price_in_text += f'• *{name}* (_{symbol}_): {price} BTC\n'
    if len(args) == 1:
        price_in_text = price_in_text[2:]
        if not not_found:
            price_in_text = '> Showing _price in BTC_\n'+price_in_text
    else:
        price_in_text = '> Showing _prices in BTC_\n'+price_in_text
    bot.send_message(chat_id=update.message.chat_id, text=price_in_text, parse_mode=telegram.ParseMode.MARKDOWN)

def get_mkt_cap_by_command(bot, update, args):
    bot.send_chat_action(chat_id=update.message.chat_id, action=telegram.ChatAction.TYPING)
    if len(args) == 0:
        total_mkt_cap   = get_global_data()['total_market_cap_usd']
        total_mkt_cap   = int(total_mkt_cap)
        mkt_cap_in_text = f'Crypto\'s total market cap is:\nUS$ {total_mkt_cap:,}'
    else:
        not_found = False
        coins = get_coins()
        mkt_cap_in_text = ''
        for arg in args:
            arg = arg.upper()
            if arg not in coins:
                coin = get_coin_by_id(arg)
                if 'id' in coin:
                    name    = coin['name']
                    symbol  = coin['symbol']
                    mkt_cap = int(float(coin['market_cap_usd']))
                else:
                    mkt_cap_in_text += f'• _{arg}_ not found\n'
                    not_found = True
                    continue
            else:
                name    = coins[arg]['name']
                symbol  = coins[arg]['symbol']
                mkt_cap = int(float(coins[arg]['market_cap_usd']))
            mkt_cap_in_text += f'• *{name}* (_{symbol}_): US$ {mkt_cap:,}\n'
        if len(args) == 1:
            mkt_cap_in_text = mkt_cap_in_text[2:]
            if not not_found:
                mkt_cap_in_text = '> Showing _market cap in USD_\n'+mkt_cap_in_text
        else:
            mkt_cap_in_text = '> Showing _market caps in USD_\n'+mkt_cap_in_text
    bot.send_message(chat_id=update.message.chat_id, text=mkt_cap_in_text, parse_mode=telegram.ParseMode.MARKDOWN)

def get_volume_by_command(bot, update, args):
    bot.send_chat_action(chat_id=update.message.chat_id, action=telegram.ChatAction.TYPING)
    if len(args) == 0:
        total_volume   = get_global_data()['total_24h_volume_usd']
        total_volume   = int(total_volume)
        volume_in_text = f'Crypto\'s total 24h-volume is:\nUS$ {total_volume:,}'
    else:
        not_found = False
        coins = get_coins()
        volume_in_text = ''
        for arg in args:
            arg = arg.upper()
            if arg not in coins:
                coin = get_coin_by_id(arg)
                if 'id' in coin:
                    name    = coin['name']
                    symbol  = coin['symbol']
                    volume  = int(float(coin['24h_volume_usd']))
                else:
                    volume_in_text += f'• _{arg}_ not found\n'
                    not_found = True
                    continue
            else:
                name    = coins[arg]['name']
                symbol  = coins[arg]['symbol']
                volume  = int(float(coins[arg]['24h_volume_usd']))
            volume_in_text += f'• *{name}* (_{symbol}_): US$ {volume:,}\n'
        if len(args) == 1:
            volume_in_text = volume_in_text[2:]
            if not not_found:
                volume_in_text = '> Showing _24h-volume in USD_\n'+volume_in_text
        else:
            volume_in_text = '> Showing _24h-volumes in USD_\n'+volume_in_text
    bot.send_message(chat_id=update.message.chat_id, text=volume_in_text, parse_mode=telegram.ParseMode.MARKDOWN)

def get_btc_dominance_by_command(bot, update):
    bot.send_chat_action(chat_id=update.message.chat_id, action=telegram.ChatAction.TYPING)
    btc_dominance = get_global_data()['bitcoin_percentage_of_market_cap']
    bot.send_message(chat_id=update.message.chat_id, text=f'Bitcoin\'s dominance is: {btc_dominance}%')

def get_news_by_command(bot, update):
    bot.send_chat_action(chat_id=update.message.chat_id, action=telegram.ChatAction.TYPING)
    news = get_news()
    for entry_idx, entry in enumerate(news[:5]):
        title   = entry['title']
        summary = entry['summary']
        link    = entry['link']
        if entry_idx == 0:
            bot.send_message(chat_id=update.message.chat_id,
                             text=f'*{title}*\n{summary}\n\n{link}',
                             parse_mode=telegram.ParseMode.MARKDOWN)
        else:
            bot.send_message(chat_id=update.message.chat_id,
                             text=f'*{title}*\n{summary}\n\n{link}',
                             parse_mode=telegram.ParseMode.MARKDOWN,
                             disable_notification=True)

def get_reddit_by_command(bot, update, args):
    bot.send_chat_action(chat_id=update.message.chat_id, action=telegram.ChatAction.TYPING)
    if len(args) == 0:
        f_name = bot.get_chat(update.message.chat_id)['first_name']
        f_name = '' if not f_name else f', {f_name}'
        messages = [
            f'Hey{f_name}! '+emojize(':wave:', use_aliases=True) ,
            'It seems like you were trying to retrieve some Reddit posts, is that correct?' ,
            'Well, I think you forgot to tell me from which subreddits you want them... But don\'t worry—let\'s figure it out!' ,
            'Try typing...' ,
            '_/reddit bitcoin_' ,
            'or maybe...' ,
            '_/reddit bitcoin cryptocurrency_'
            ]
        bot.send_message(chat_id=update.message.chat_id, text=messages[0], parse_mode=telegram.ParseMode.MARKDOWN)
        for message in messages[1:-1]:
            bot.send_message(chat_id=update.message.chat_id, text=message, parse_mode=telegram.ParseMode.MARKDOWN, disable_notification=True)
        bot.send_message(chat_id=update.message.chat_id, text=messages[-1], parse_mode=telegram.ParseMode.MARKDOWN, disable_notification=True, reply_markup=telegram.ForceReply())
        return
    for arg in args:
        subreddit = reddit.subreddit(arg)
        try:
            list(subreddit.hot(limit=5))
        except Exception:
            bot.send_message(chat_id=update.message.chat_id,
                 text=f'<i>/r/{arg}</i> not found',
                 parse_mode=telegram.ParseMode.HTML,
                 disable_notification=True)
            continue
        for submission in subreddit.hot(limit=5):
            title = submission.title
            link  = submission.url
            bot.send_message(chat_id=update.message.chat_id,
                 text=f'{title}\n\n{link}',
                 parse_mode=telegram.ParseMode.HTML,
                 disable_notification=True)

def auto_news(bot, job):
    news_db  = shelve.open('news')
    users_db = shelve.open('users')
    news     = {}
    for news_portal in ['cd', 'ct', 'ccn']:
        news[news_portal] = get_news(news_portal)[0]
        if news_db[news_portal] == news[news_portal]:
            continue
        title = news[news_portal]['title']
        link  = news[news_portal]['link']
        for user in users_db:
            if users_db[user]['auto_news']:
                try:
                    bot.send_message(chat_id=int(user),
                                     text=f'{title}\n\n{link}',
                                     parse_mode=telegram.ParseMode.MARKDOWN)
                except Exception:
                    continue
        news_db[news_portal] = news[news_portal]
    news_db.close()
    users_db.close()

def auto_news_on(bot, update):
    bot.send_chat_action(chat_id=update.message.chat_id, action=telegram.ChatAction.TYPING)
    users_db        = shelve.open('users')
    chat            = str(update.message.chat_id)
    f_name = bot.get_chat(update.message.chat_id)['first_name']
    f_name = '' if not f_name else f', {f_name}'
    if users_db[chat]['auto_news']:
        message = f'My <i>AutoNews</i> function is already on{f_name}.\nIf you are trying to turn it off, type /news_off instead.'
        bot.send_message(chat_id=update.message.chat_id, text=message, parse_mode=telegram.ParseMode.HTML)
    else:
        message1 = f'Ok{f_name}. Turning on <i>AutoNews</i>...'
        bot.send_message(chat_id=update.message.chat_id, text=message1, parse_mode=telegram.ParseMode.HTML)
        edited_user = {}
        for data in users_db[chat]:
            if data == 'auto_news':
                edited_user[data] = True
                continue
            edited_user[data] = users_db[chat][data]
        users_db[chat] = edited_user
        message2 = f'Done! '+emojize(':wink:', use_aliases=True)+f'\nAnytime you wish to turn it off again, just type /autonews or /news_off.'
        bot.send_message(chat_id=update.message.chat_id, text=message2, parse_mode=telegram.ParseMode.HTML)
    users_db.close()

def auto_news_off(bot, update):
    bot.send_chat_action(chat_id=update.message.chat_id, action=telegram.ChatAction.TYPING)
    users_db        = shelve.open('users')
    chat            = str(update.message.chat_id)
    f_name = bot.get_chat(update.message.chat_id)['first_name']
    f_name = '' if not f_name else f', {f_name}'
    if not users_db[chat]['auto_news']:
        message = f'My <i>AutoNews</i> function is already off{f_name}.\nIf you are trying to turn it on, type /news_on instead.'
        bot.send_message(chat_id=update.message.chat_id, text=message, parse_mode=telegram.ParseMode.HTML)
    else:
        message1 = f'Ok{f_name}. Turning off <i>AutoNews</i>...'
        bot.send_message(chat_id=update.message.chat_id, text=message1, parse_mode=telegram.ParseMode.HTML)
        edited_user = {}
        for data in users_db[chat]:
            if data == 'auto_news':
                edited_user[data] = False
                continue
            edited_user[data] = users_db[chat][data]
        users_db[chat] = edited_user
        message2 = f'Done! '+emojize(':wink:', use_aliases=True)+f'\nAnytime you wish to turn it on again, just type /autonews or /news_on.'
        bot.send_message(chat_id=update.message.chat_id, text=message2, parse_mode=telegram.ParseMode.HTML)
    users_db.close()

def auto_news_toggle(bot, update):
    bot.send_chat_action(chat_id=update.message.chat_id, action=telegram.ChatAction.TYPING)
    users_db        = shelve.open('users')
    chat            = str(update.message.chat_id)
    if users_db[chat]['auto_news']:
        users_db.close()
        auto_news_off(bot, update)
    else:
        users_db.close()
        auto_news_on(bot, update)

def jokes(bot, update):
    bot.send_chat_action(chat_id=update.message.chat_id, action=telegram.ChatAction.TYPING)
    from jokes_db import jks
    joke = jks[randint(0, len(jks)-1)]
    bot.send_message(chat_id=update.message.chat_id, text=joke['joke'][0], parse_mode=telegram.ParseMode.HTML)
    for line in joke['joke'][1:]:
        bot.send_message(chat_id=update.message.chat_id, text=line, parse_mode=telegram.ParseMode.HTML, disable_notification=True)
    bot.send_message(chat_id=update.message.chat_id, text='Sent by <i>{}</i>'.format(joke['author']), parse_mode=telegram.ParseMode.HTML, disable_notification=True)
    del jks

def send_joke(bot, update, args):
    bot.send_chat_action(chat_id=update.message.chat_id, action=telegram.ChatAction.TYPING)
    f_name = bot.get_chat(update.message.chat_id)['first_name']
    f_name = '' if not f_name else f', {f_name}'
    if len(args) <= 3:
        bot.send_message(chat_id=update.message.chat_id, text=f'Not a real joke{f_name}...\nPlease try again with a good one.', parse_mode=telegram.ParseMode.HTML)
    date   = update.message['date']
    print(update.message)
    author = update.message['chat']['username']
    joke   = u' '.join(args).encode('utf-8').strip()
    new_jokes_db = open('new_jokes_db.csv')
    new_jokes_db_reader = csv.reader(new_jokes_db)
    unread_new_jokes = list(new_jokes_db_reader)
    new_jokes_db.close()
    new_jokes_db = open('new_jokes_db.csv', 'w', newline='')
    new_jokes_db_writer = csv.writer(new_jokes_db)
    for joke_data in unread_new_jokes:
        new_jokes_db_writer.writerow(joke_data)
    try:
        new_jokes_db_writer.writerow([date, joke, author])
    except Exception as err:
        debug(bot, update, err)
    new_jokes_db.close()
    message = f'Thanks{f_name}! Your joke has been submitted. '+emojize(':thumbsup:', use_aliases=True)
    bot.send_message(chat_id=update.message.chat_id, text=message, parse_mode=telegram.ParseMode.HTML)

def share(bot, update):
    f_name = bot.get_chat(update.message.chat_id)['first_name']
    f_name = '' if not f_name else f', {f_name}'
    bot.send_message(chat_id=update.message.chat_id, text='Yay! I\'m being shared!', parse_mode=telegram.ParseMode.HTML)
    bot.send_message(chat_id=update.message.chat_id, text='Send the following link to your friends by copy-pasting it wherever you want.', parse_mode=telegram.ParseMode.HTML,
                     disable_notification=True)
    bot.send_message(chat_id=update.message.chat_id, text='https://t.me/crpytobot', parse_mode=telegram.ParseMode.HTML, disable_notification=True)
    bot.send_message(chat_id=update.message.chat_id, text='You\'re awesome{f_name}! To the moon!', parse_mode=telegram.ParseMode.HTML, disable_notification=True)

def debug(bot, update, error):
    f_name = bot.get_chat(update.message.chat_id)['first_name']
    f_name = '' if not f_name else f', {f_name}'
    message = f'''Oh oh{f_name}, something went wrong...
But don't worry—I've already notified my masters. They'll take care of that for us.
If you want to speed up our debugging process, please upload the following error message to my <a href="http://google.com">GitHub page</a>.'''
    bot.send_message(chat_id=update.message.chat_id, text=message, parse_mode=telegram.ParseMode.HTML, disable_web_page_preview=True)
    bot.send_message(chat_id=update.message.chat_id, text=error, parse_mode=telegram.ParseMode.HTML, disable_notification=True)

def handle_unknown_command(bot, update):
    bot.send_chat_action(chat_id=update.message.chat_id, action=telegram.ChatAction.TYPING)
    f_name = bot.get_chat(update.message.chat_id)['first_name']
    f_name = '' if not f_name else f', {f_name}'
    message = f'I didn\'t understand that command{f_name}. Sorry '+emojize(':disappointed:', use_aliases=True)+'\nIf you need help, type /help.'
    bot.send_message(chat_id=update.message.chat_id, text=message)

def help_bot(bot, update):
    bot.send_chat_action(chat_id=update.message.chat_id, action=telegram.ChatAction.TYPING)
    f_name  = bot.get_chat(update.message.chat_id)['first_name']
    f_name = '' if not f_name else f', {f_name}'
    chat_id          = str(update.message.chat_id)
    users_db         = shelve.open('users')
    auto_news_status = 'on✔' if users_db[chat_id]['auto_news'] else 'off✖'
    emojis           = [emojize(':wave:', use_aliases=True), emojize(':green_heart:', use_aliases=True)]
    users_db.close()
    message = f'''Hi there{f_name}! {emojis[0]}

Well, as you might have noticed, I'm not AI-powered yet, so you still need to control me by pre-programmed commands. These commands are riiiiiight here:

<b>Coins data</b>
For all the commands below, you should be able to work with multiple coins. To do that, simply separate their symbols/names with spaces.
Additionally, any coin's symbol or name is accepted.
Note: if your coin's full name has more than one name, please use its symbol.

/price <i>coin</i> - get <i>coin</i>'s price in US Dollars and its variation in the last 24 hours
/pricebtc <i>coin</i> - get <i>coin</i>'s price in Bitcoins
/mktcap - get crypto's total market capitalisation in US Dollars
/mktcap <i>coin</i> - get <i>coin</i>'s market capitalisation in US Dollars
/volume - get crypto's total trade volume in the last 24 hours, in US Dollars
/volume <i>coin</i> - get <i>coin</i>'s trade volume in the last 24 hours, in US Dollars

<b>News and information</b>
You should automatically receive news from the crypto space as soon as they come out: AutoNews feature is on by default.
It can however be disabled and re-enabled with the commands /news_off and /news_on.
Right now, AutoNews is: {auto_news_status}

/news - get the last 5 top news from CoinDesk
/autonews - turn AutoNews on or off
/reddit <i>subreddit</i> - get the best 5 hot posts from <i>subreddit</i>
(Works with any and multiple subreddits)

<b>Others</b>
/btcdominance - get Bitcoin's current market-share percentage
/jokes - get a crypto joke
/sendjoke <i>joke</i> - improve my jokes database by sending me your best crypto joke

<b>Portfolio management</b>
To be implemented.

<b>About me</b>
If you have any more doubts or concerns, please feel free to upload your questions to my <a href="http://google.com">GitHub page</a>.

Made with {emojis[1]} by the crypto community, for the crypto community.
'''
    bot.send_message(chat_id=update.message.chat_id, text=message, parse_mode=telegram.ParseMode.HTML, disable_web_page_preview=True)

start_message_handler = telegram.ext.CommandHandler('start', start_message)
d.add_handler(start_message_handler)

get_price_by_command_handler = telegram.ext.CommandHandler('price', get_price_by_command, pass_args=True)
d.add_handler(get_price_by_command_handler)

get_price_btc_by_command_handler = telegram.ext.CommandHandler('pricebtc', get_price_btc_by_command, pass_args=True)
d.add_handler(get_price_btc_by_command_handler)

get_mkt_cap_by_command_handler = telegram.ext.CommandHandler('mktcap', get_mkt_cap_by_command, pass_args=True)
d.add_handler(get_mkt_cap_by_command_handler)

get_volume_by_command_handler = telegram.ext.CommandHandler('volume', get_volume_by_command, pass_args=True)
d.add_handler(get_volume_by_command_handler)

get_btc_dominance_by_command_handler = telegram.ext.CommandHandler('btcdominance', get_btc_dominance_by_command)
d.add_handler(get_btc_dominance_by_command_handler)

get_news_by_command_handler = telegram.ext.CommandHandler('news', get_news_by_command)
d.add_handler(get_news_by_command_handler)

j.run_repeating(auto_news, interval=1800, first=180)

auto_news_toggle_handler = telegram.ext.CommandHandler('autonews', auto_news_toggle)
d.add_handler(auto_news_toggle_handler)

auto_news_on_handler = telegram.ext.CommandHandler('news_on', auto_news_on)
d.add_handler(auto_news_on_handler)

auto_news_off_handler = telegram.ext.CommandHandler('news_off', auto_news_off)
d.add_handler(auto_news_off_handler)

reddit_handler = telegram.ext.CommandHandler('reddit', get_reddit_by_command, pass_args=True)
d.add_handler(reddit_handler)

jokes_handler = telegram.ext.CommandHandler('jokes', jokes)
d.add_handler(jokes_handler)

send_joke_handler = telegram.ext.CommandHandler('sendjoke', send_joke, pass_args=True)
d.add_handler(send_joke_handler)

help_bot_handler = telegram.ext.CommandHandler('help', help_bot)
d.add_handler(help_bot_handler)

handle_unknown_command_handler = telegram.ext.MessageHandler(telegram.ext.Filters.command, handle_unknown_command)
d.add_handler(handle_unknown_command_handler)

u.start_polling()

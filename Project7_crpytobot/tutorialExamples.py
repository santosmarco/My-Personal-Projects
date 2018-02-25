from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, InlineQueryHandler, BaseFilter
from telegram import InlineQueryResultArticle, InputTextMessageContent
import logging

#Para fins de debugging...
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

#Incializando o bot...
#O [updater] checara por novas atualizacoes de interacao com o bot
updater = Updater(token='419141016:AAGO0XfoJEEaiFRw6bdiHzHucqim5AQqoBw')
#O [dispatcher] ficara responsavel por enviar respostas as interacoes
dispatcher = updater.dispatcher
#O [j] ficara responsavel por lancar comandos em determinados tempos ou depois de delays programados
j = updater.job_queue

class FilterAwesome(BaseFilter):
    def filter(self, message):
        return 'python-telegram-bot is awesome' in message.text

filter_awesome = FilterAwesome()

#Definindo uma funcao que respondera a interacao /start...
def start(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text="I'm a bot, please talk to me!")

#Definindo uma funcao para responder a mensagem que tiver a interacao /start
def callback_start(bot, update, args):
    user_says = ' '.join(args)
    update.message.reply_text('Welcome to my awesome bot!\nYou said: '+user_says)

#Definindo uma funcao que respondera a textos comuns com o proprio texto...
def echo(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text=update.message.text)

#Definindo uma funcao que transforma os argumentos de uma bot call em caps
def caps(bot, update, args):
    text_caps = ' '.join(args).upper()
    bot.send_message(chat_id=update.message.chat_id, text=text_caps)

def inline_caps(bot, update):
    query = update.inline_query.query
    if not query:
        return
    results = []
    results.append(
        InlineQueryResultArticle(
            id=query.upper(),
            title='Caps',
            input_message_content=InputTextMessageContent(query.upper())
        )
    )
    bot.answer_inline_query(update.inline_query.id, results)

#Definindo uma funcao que respondera interacoes desconhecidas...
def unknown(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text="Sorry, I didn't understand that command.")

#Definindo uma funcao para enviar uma mensagem a cada minuto a um chat especificado...
def callback_minute(bot, job):
    bot.send_message(chat_id=116049273, text='One message every minute.')

#Definindo uma funcao para ser executada uma so vez, com um delay
def callback_30(bot, job):
    bot.send_message(chat_id='116049273',
                     text='A single message with 30s delay')

#Definindo uma funcao que enviara uma mensagem a cada segundo, depois a dois segundos, tres... ate 10,
#em que entao o job sera removido.
def callback_increasing(bot, job):
    bot.send_message(chat_id='116049273',
                     text='Sending messages with increasing delay up to 10s, then stops.')
    job.interval += 1.0
    if job.interval > 10.0:
        job.schedule_removal()

#Definindo uma funcao para daqui a 60 segundos mandar uma mensagem ao usuario que
#pedir ao bot uma bot call /timer (mais a frente...)
def callback_alarm(bot, job):
    bot.send_message(chat_id=job.context,
                     text='BEEP')
def callback_timer(bot, update, job_queue):
    bot.send_message(chat_id=update.message.chat_id,
                     text='Setting a timer for 1 minute!')
    job_queue.run_once(callback_alarm, 60, context=update.message.chat_id)

def awesome_handler_callback(bot, update):
    update.message.reply_text('Obrigado')

#Dizendo ao bot que a funcao [start] (arg. 2) deve ser a resposta da interacao /start (arg. 1)
start_handler = CommandHandler('start', start)
#Adicionando essa ordem ao dispatcher para que ele fique tambem sabendo disso
dispatcher.add_handler(start_handler)

#Mesma coisa para a funcao [callback_start]...
start2_handler = CommandHandler('start2', callback_start, pass_args=True)
dispatcher.add_handler(start2_handler)

#Dizendo ao bot que a funcao [echo] deve ser a resposta de textos comuns (todos)
echo_handler = MessageHandler(Filters.text, echo)
#Adicionando essa ordem ao dispatcher...
dispatcher.add_handler(echo_handler)

#Dizendo ao bot que a funcao [caps] deve ser a resposta da interacao /caps + argumentos (pass_args=True)
caps_handler = CommandHandler('caps', caps, pass_args=True)
dispatcher.add_handler(caps_handler)

inline_caps_handler = InlineQueryHandler(inline_caps)
dispatcher.add_handler(inline_caps_handler)

#Dizendo ao bot que a funcao [callback_timer] + o job_queue atual deve ser a resposta da interacao /timer
timer_handler = CommandHandler('timer', callback_timer, pass_job_queue=True)
dispatcher.add_handler(timer_handler)

awesome_handler = MessageHandler(filter_awesome, awesome_handler_callback)
dispatcher.add_handler(awesome_handler)

#Dizendo ao bot que a funcao [unknown] deve ser a resposta de qualquer bot call desconhecida
unknown_handler = MessageHandler(Filters.command, unknown)
dispatcher.add_handler(unknown_handler)

#Dizendo ao bot para executar a funcao [callback_minute] a cada 60 segundos, sendo o primeiro no tempo 0
job_minute = j.run_repeating(callback_minute, interval=60, first=0)

#Dizendo ao bot para executar a funcao [callback_30] daqui a 30 segundos
j.run_once(callback_30, 30)

job_minute.enabled = False       # Temporariamente desabilitando o job da mensagem/minuto
                                 # (pode trocar para True quando quiser reativar)
job_minute.schedule_removal()    # Remove o job permanentemente
                                 # (some da memoria)

#Chama a funcao [callback_increasing] daqui a um segundo e ai depois ela vai atuando...
j.run_repeating(callback_increasing, 1)

#Inicia o bot...
updater.start_polling()

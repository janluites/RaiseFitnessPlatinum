import telebot
import lists


bot = telebot.TeleBot(lists.token)

@bot.message_handler(content_types=['text'])
def handle_text(message):
    if message.chat.type == 'supergroup':
        print "Name: %s" % message.from_user.first_name
        print "User ID: %s" % message.from_user.id
        print "Supergroup ID: %s" % message.chat.id
        print 10*"="
    else:
        print "This is not supergroup"


while True:
    try:      
        bot.polling(none_stop=True)
    except Exception as e:
        pass

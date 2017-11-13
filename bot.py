# -*- coding: utf-8 -*-

import time
import telebot
import game
import lists
import logging
import instagram_engine
import datetime
from dbhelper import DBHelper
from collections import OrderedDict
from apscheduler.schedulers.background import BackgroundScheduler


logger = telebot.logger
telebot.logger.setLevel(logging.DEBUG)

scheduler = BackgroundScheduler()


bot = telebot.TeleBot(lists.token)
db = DBHelper()

# =============== Engine =============== #


def check_user(tlgrm_id):
    get_user = db.get_tlgrm_user(tlgrm_id)
    if get_user is not None:
        return True
    else:
        return False


def add_user(tlgrm_id):
    get_user = db.get_tlgrm_user(tlgrm_id)
    if get_user is None:
        db.add_tlgrm_user(tlgrm_id)


def warning(tlgrm_id):
    if db.get_warnings(tlgrm_id) < 3:
        db.add_warning(tlgrm_id)
    else:
        bot.kick_chat_member(lists.chat_id, tlgrm_id)


def get_sorted_list():
    curr_points = {}
    for insta_username in lists.DICT.values():
        points = db.get_points_by_insta(insta_username)
        curr_points[insta_username] = points
    unsort_dict = OrderedDict(sorted(curr_points.items(), key=lambda x: x[1]))
    lists.CURR_POINTS = dict(OrderedDict(reversed(list(unsort_dict.items()))))


def stage_one():
    text = "\xE2\x9C\xA8 *STAGE 1. Drop time* \xE2\x9C\xA8\n\n" \
           "First time users, message me your IG username like this *@username*\nRegular members, type /in"
    bot.send_message(lists.chat_id, text, parse_mode='Markdown')
    lists.collecting = True
    lists.game_active = True
    time.sleep(1200)    
    text = '''\xF0\x9F\x94\xB5 *Round is about to start in 10 minutes!* \xF0\x9F\x94\xB5\nIf you're a new member please message to bot your @username to be added to the list! After that come back and type /in to be added to the round'''
    bot.send_message(lists.chat_id, text, parse_mode='Markdown')
    time.sleep(600)    
    stage_two()


def stage_two():
    lists.collecting = False
    game.save_results()
    get_sorted_list()
    instagram_engine.get_ids(lists.DICT.values())
    lists.TID_IID_DICT = dict(zip(lists.DICT.keys(), lists.ID_LIST))
    if len(lists.CURR_POINTS.keys()) > 1:
        text = "\xF0\x9F\x92\xA5 *STAGE 2. Like and comment* \xF0\x9F\x92\xA5\n\n"
        for insta_username in lists.CURR_POINTS.keys():
            text += '*@%s* \n' % insta_username
        bot.send_message(lists.chat_id, text, parse_mode='Markdown')
        print lists.DICT
        time.sleep(3600)
        text = "\xE2\x8C\x9B *Checking results...* \xE2\x8C\x9B\n\n"
        bot.send_message(lists.chat_id, text, parse_mode='Markdown')
        results()        
    else:
        lists.game_active = False
        lists.DICT = {}
        lists.TID_IID_DICT = {}
        lists.CURR_POINTS = {}
        bot.send_message(lists.chat_id, '\xF0\x9F\x98\x9E Sorry, I need more users to play this game')



def results():
    if game.check_results():
        not_engaged = []        
        for tlgrm_id in lists.POINTS.keys():
            if tlgrm_id == lists.admin:
                text = '\xF0\x9F\x94\xB5 Round Has Ended \xF0\x9F\x94\xB5\n' \
                       '\xF0\x9F\xA4\x96 You are admin so I don`t check your engagement'
                bot.send_message(tlgrm_id, text)
            elif lists.POINTS[tlgrm_id] >= ((len(lists.DICT)-1)/100.)*85:
                db.add_points(tlgrm_id, 1)
                points = db.get_points_by_tele(tlgrm_id)
                text = '\xF0\x9F\x94\xB5 Round Has Ended \xF0\x9F\x94\xB5\nYou completed this round successfully\n' \
                       'Now you have %s bonus points' % points
                bot.send_message(tlgrm_id, text)
            else:
                warning(tlgrm_id)
                not_engaged.append(lists.DICT[tlgrm_id])
                warnings = db.get_warnings(tlgrm_id)
                text = '\xF0\x9F\x94\xB5 Round Has Ended \xF0\x9F\x94\xB5\nWarning! You don`t completed this round\n' \
                       'You have %s/5 warning points' % warnings
                bot.send_message(tlgrm_id, text)        
        if len(not_engaged) > 0:
            text = 'Users that not engaged:\n\n'
            for insta_username in not_engaged:
                text = text + '@%s\n' % insta_username
            bot.send_message(lists.chat_id, text)
        text = "\xE2\x9D\x8C *Round completed!* \xE2\x9D\x8C"
        bot.send_message(lists.chat_id, text, parse_mode='Markdown')
        lists.DICT = {}
        lists.TID_IID_DICT = {}
        lists.CURR_POINTS = {}
        lists.POINTS = {}
        lists.game_active = False
    else:
        bot.send_message(lists.chat_id, '\xF0\x9F\x98\x9E Game error... contact @Bodybuildingert', parse_mode='Markdown')


# =============== Commands =============== #


#@bot.message_handler(content_types=['text'])
#def handle_text(message):
#    print message


@bot.message_handler(commands=['start'])
def handle_text(message):
    if message.chat.type == "private":
        tlgrm_id = message.from_user.id
        if check_user(tlgrm_id) is False:
            bot.send_message(tlgrm_id, '\xF0\x9F\xA4\x96 Contact *@Bodybuildingert* to join the game', parse_mode='Markdown')
        else:
            bot.send_message(tlgrm_id, lists.rules)


@bot.message_handler(commands=['rules'])
def handle_text(message):
    if message.chat.type == "private":
        tlgrm_id = message.from_user.id
        if check_user(tlgrm_id):
            bot.send_message(tlgrm_id, lists.rules)


@bot.message_handler(commands=['status'])
def handle_text(message):
    if message.chat.type == "private":
        tlgrm_id = message.from_user.id
        if check_user(tlgrm_id) and lists.game_active and lists.collecting:
            insta_user = db.get_insta_user(tlgrm_id)
            if insta_user != 'none':                
                text = 'Stage 1 has started, type /in to join in with username: *@%s*' % insta_user
                bot.send_message(tlgrm_id, text, parse_mode='Markdown')
            else:
                text = 'Stage 1 has started. You don`t have saved usernames to join'
                bot.send_message(tlgrm_id, text)
        elif check_user(tlgrm_id) and lists.game_active and lists.collecting is False:
            insta_user = db.get_insta_user(tlgrm_id)
            if insta_user != 'none':
                text = 'Stage 2 has already started. Wait for the next round and type /in' \
                       ' to join in with username: *@%s*' % insta_user
                bot.send_message(tlgrm_id, text, parse_mode='Markdown')
            else:
                text = 'Stage 2 has already started. You don`t have saved usernames to join'
                bot.send_message(tlgrm_id, text)
        elif check_user(tlgrm_id) and lists.game_active is False:
            insta_user = db.get_insta_user(tlgrm_id)
            if insta_user != 'none':
                text = 'Round has not started yet. Type /in at name submission period to use username: *@%s*' % insta_user
                bot.send_message(tlgrm_id, text, parse_mode='Markdown')
            else:
                text = 'Round has not started yet. You don`t have saved usernames to join.'
                bot.send_message(tlgrm_id, text)


@bot.message_handler(commands=['next'])
def handle_text(message):
    tlgrm_id = message.from_user.id
    if message.chat.type == "private" and check_user(tlgrm_id):
        try:
            now_time = datetime.datetime.now().replace(microsecond=0)
            next_round = scheduler.get_jobs()[0].next_run_time.strftime("%Y-%m-%d %H:%M:%S")
            next_round = datetime.datetime.strptime(str(next_round), "%Y-%m-%d %H:%M:%S")
            next_round_time = next_round - now_time
            next_round_time = datetime.datetime.strptime(str(next_round_time), "%H:%M:%S")
            next_round_time = next_round_time.strftime("%H:%M")
            next_round_time = next_round_time.split(':')
            if lists.game_active is False:
                text = 'Name submissions starts in *%s hours* and *%s minutes*' \
                       % (int(next_round_time[0]), int(next_round_time[1]))
                bot.send_message(tlgrm_id, text, parse_mode='Markdown')
            elif lists.game_active and lists.collecting:
                text = 'Name submissions has started.' \
                       ' Type /in to join the round. Next round starts at *%s hours* and *%s minutes*' \
                       % (int(next_round_time[0]), int(next_round_time[1]))
                bot.send_message(tlgrm_id, text, parse_mode='Markdown')
            elif lists.game_active and lists.collecting is False:
                text = 'Round has started. Wait for the next round to join. ' \
                       'Next round starts at *%s hours* and *%s minutes*' \
                       % (int(next_round_time[0]), int(next_round_time[1]))
                bot.send_message(tlgrm_id, text, parse_mode='Markdown')
        except IndexError:
            pass
        

@bot.message_handler(commands=['rounds'])
def handle_text(message):
    tlgrm_id = message.from_user.id
    if message.chat.type == "private" and check_user(tlgrm_id):
        try:
            now_time = datetime.datetime.now().replace(microsecond=0)
            next_rounds = []
            for job in scheduler.get_jobs():
                next_time = job.next_run_time.strftime("%Y-%m-%d %H:%M:%S")
                next_rounds.append(str(next_time))
            n = 0
            text = ''
            for next_round in next_rounds:
                n += 1
                next_round = datetime.datetime.strptime(str(next_round), "%Y-%m-%d %H:%M:%S")
                next_round_time = next_round - now_time
                next_round_time = datetime.datetime.strptime(str(next_round_time), "%H:%M:%S")
                next_round_time = next_round_time.strftime("%H:%M")
                next_round_time = next_round_time.split(':')
                text += "*" + str(n) + ".* Round starts in *%s hours* and *%s minutes*\n" \
                        % (int(next_round_time[0]), int(next_round_time[1]))
            bot.send_message(tlgrm_id, text, parse_mode='Markdown')
        except IndexError:
            pass


@bot.message_handler(commands=['points'])
def handle_text(message):
    tlgrm_id = message.from_user.id
    if message.from_user.id == lists.admin:
        bot.send_message(tlgrm_id, '\xF0\x9F\xA4\x96 You are admin. You don`t have points')
    elif message.chat.type == "private":
        if check_user(tlgrm_id):
            points = db.get_points_by_tele(tlgrm_id)
            if points is None:
                points = 0
            bot.send_message(tlgrm_id, '\xF0\x9F\x93\x9D Your score is: %s' % points)


@bot.message_handler(commands=['warnings'])
def handle_text(message):
    tlgrm_id = message.from_user.id
    if message.from_user.id == lists.admin:
        bot.send_message(tlgrm_id, '\xF0\x9F\xA4\x96 You are admin. You don`t have warnings')
    elif message.chat.type == "private":
        if check_user(tlgrm_id):
            warnings = db.get_warnings(tlgrm_id)
            if warnings is None:
                warnings = 0
            bot.send_message(tlgrm_id, '\xF0\x9F\x9A\xAB Your have %s/5 warnings' % warnings)


@bot.message_handler(commands=['in'])
def handle_text(message):
    chat_id = message.chat.id
    tlgrm_id = message.from_user.id
    try:
        if tlgrm_id == lists.admin and tlgrm_id not in lists.UNFORM_DICT.keys() and lists.collecting or \
           tlgrm_id not in lists.UNFORM_DICT.keys() and chat_id == lists.chat_id and lists.collecting:
            if db.get_insta_user(tlgrm_id) == "none":
                bot.send_message(tlgrm_id, '\xE2\x9D\x97 You don`t have saved Instagram username')
            else:
                insta_username = db.get_insta_user(tlgrm_id).replace('@', '')
                if insta_username in lists.UNFORM_DICT.values():
                    bot.send_message(tlgrm_id, '\xE2\x9D\x97 This username has already joined the round!')
                elif tlgrm_id == lists.admin:
                    bot.send_message(tlgrm_id, '\xF0\x9F\xA4\x96 Added to the top of the list!')
                    game.collecting_usernames(tlgrm_id, insta_username)
                else:
                    bot.send_message(tlgrm_id, '\xE2\xAD\x90 You`re in for the next round')
                    game.collecting_usernames(tlgrm_id, insta_username)
        elif tlgrm_id == lists.admin and tlgrm_id in lists.UNFORM_DICT.keys() and lists.collecting or \
             tlgrm_id in lists.UNFORM_DICT.keys() and chat_id == lists.chat_id and lists.collecting:
            bot.send_message(tlgrm_id, '\xE2\x9D\x97 You have already in for the next round')
    except Exception:
        print(Exception)
        pass
    

@bot.message_handler(commands=['out'])
def handle_text(message):
    chat_id = message.chat.id
    tlgrm_id = message.from_user.id
    if message.chat.type == "private" and tlgrm_id == lists.admin \
            and lists.collecting and tlgrm_id in lists.UNFORM_DICT.keys():
        del lists.UNFORM_DICT[tlgrm_id]
        bot.send_message(tlgrm_id, '\xF0\x9F\xA4\x96 You left the round')
    elif chat_id == lists.chat_id and lists.collecting and tlgrm_id in lists.UNFORM_DICT.keys():
        del lists.UNFORM_DICT[tlgrm_id]
        bot.send_message(tlgrm_id, '\xE2\x9D\x8C You left the round')


@bot.message_handler(commands=['list'])
def handle_text(message):
    if message.chat.type == "private":
        tlgrm_id = message.from_user.id
        if check_user(tlgrm_id) and lists.game_active and lists.collecting is False:
            text = 'List of all users\n\n'
            for insta_user in lists.CURR_POINTS.keys():
                text += "*@" + insta_user + "*\n"
            bot.send_message(tlgrm_id, text, parse_mode='Markdown')


@bot.message_handler(commands=['check'])
def handle_text(message):
    if message.chat.type == "private":
        tlgrm_id = message.from_user.id
        if check_user(tlgrm_id) and lists.game_active and lists.collecting is False and tlgrm_id in lists.TID_IID_DICT.keys():
            bot.send_message(tlgrm_id, '*Checking...*', parse_mode='Markdown')
            insta_self_id = lists.TID_IID_DICT[tlgrm_id]
            text = "Your engagement:\n\n"
            points = 0
            for insta_id in lists.TID_IID_DICT.values():
                if insta_id == insta_self_id:
                    pass
                else:
                    insta_username = lists.TID_IID_DICT.keys()[lists.TID_IID_DICT.values().index(insta_id)]
                    insta_username = lists.DICT[insta_username]
                    shortcode = instagram_engine.get_shortcode(insta_id)
                    LIKES_LIST = instagram_engine.get_likes(shortcode)
                    COMMENTS_LIST = instagram_engine.get_comments(shortcode)
                    try:
                        if str(insta_self_id) in LIKES_LIST and str(insta_self_id) in COMMENTS_LIST:
                            text += '*%s*: Done\n' % insta_username
                            points += 1
                        else:
                            text += '*%s*: None\n' % insta_username
                    except Exception:
                        text += '*%s*: Done\n' % insta_username
                        points += 1
                        pass
            if points != 0:
                limit = (len(lists.DICT)-1)/100.
                result = points / limit
                text = "Your result: *%s%%*" % int(result)
            else:
                text = "Your result: *0%*"
            bot.send_message(tlgrm_id, text, parse_mode='Markdown')
        elif check_user(tlgrm_id) and lists.game_active and lists.collecting and tlgrm_id in lists.TID_IID_DICT.keys():
            text = "You can use this command only during Stage 2"
            bot.send_message(tlgrm_id, text)
        elif check_user(tlgrm_id) and lists.game_active is False:
             text = "Round has not started. Use this command during Stage 2"
             bot.send_message(tlgrm_id, text)
            

@bot.message_handler(commands=['checkmore'])
def handle_text(message):
    if message.chat.type == "private":
        tlgrm_id = message.from_user.id
        if check_user(tlgrm_id) and lists.game_active and lists.collecting is False and tlgrm_id in lists.TID_IID_DICT.keys():
            bot.send_message(tlgrm_id, '*Checking...*', parse_mode='Markdown')
            insta_user = lists.DICT[tlgrm_id]
            insta_id = lists.TID_IID_DICT[tlgrm_id]
            shortcode = instagram_engine.get_shortcode(insta_id)
            LIKES_LIST = instagram_engine.get_likes(shortcode)
            COMMENTS_LIST = instagram_engine.get_comments(shortcode)
            text = "Account *%s* engagement:\n\n" % insta_user
            for ig_id in lists.TID_IID_DICT.values():
                if lists.TID_IID_DICT.keys()[lists.TID_IID_DICT.values().index(ig_id)] == lists.admin:
                    pass
                if ig_id == lists.TID_IID_DICT[tlgrm_id]:
                    pass
                else:
                    insta_username = lists.TID_IID_DICT.keys()[lists.TID_IID_DICT.values().index(ig_id)]
                    insta_username = lists.DICT[insta_username]
                    try:
                        if str(ig_id) in LIKES_LIST and str(ig_id) in COMMENTS_LIST:
                            text += "*@%s*: Done\n" % insta_username
                        else:
                            text += "*@%s*: None\n" % insta_username
                    except Exception:
                        text += '*%s*: Done\n' % insta_username
                        pass
                        # bot.send_message(tlgrm_id, 'Try again later')
            bot.send_message(tlgrm_id, text, parse_mode='Markdown')
        elif check_user(tlgrm_id) and lists.game_active and lists.collecting and tlgrm_id in lists.TID_IID_DICT.keys():
            text = "You can use this command only during Stage 2"
            bot.send_message(tlgrm_id, text)
        elif check_user(tlgrm_id) and lists.game_active is False:
             text = "Round has not started. Use this command during Stage 2"
             bot.send_message(tlgrm_id, text)


# =============== Admin Commands =============== #


@bot.message_handler(commands=['addround'])
def handle_text(message):
    tlgrm_id = message.from_user.id
    if message.chat.type == "private" and tlgrm_id == lists.admin:
        lists.add_job = True
        text = "\xF0\x9F\xA4\x96 Send me a time for new round like this h:m *(00:00-23:59)*"
        bot.send_message(tlgrm_id, text, parse_mode='Markdown')


@bot.message_handler(commands=['delround'])
def handle_text(message):
    tlgrm_id = message.from_user.id
    if message.chat.type == "private" and tlgrm_id == lists.admin:
        lists.del_job = True
        text = "\xF0\x9F\xA4\x96 Send me *Round id*\n\n"
        for round_time in lists.ROUNDS_ID.keys():
            text += '\xF0\x9F\xA4\x96 Round time: %s (*id=%s*)\n' % (round_time, lists.ROUNDS_ID[round_time])
        bot.send_message(tlgrm_id, text, parse_mode='Markdown')


@bot.message_handler(commands=['refresh'])
def handle_text(message):
    tlgrm_id = message.from_user.id
    if message.chat.type == "private" and tlgrm_id == lists.admin:
        refresh()
        bot.send_message(tlgrm_id, '\xF0\x9F\xA4\x96 All points and warning are refreshed!')


@bot.message_handler(content_types=['text'])
def handle_text(message):
    chat_id = message.chat.id
    tlgrm_id = message.from_user.id
    if message.chat.type == "private" and lists.add_job and tlgrm_id == lists.admin \
            and message.text[0].isdigit():
        try:
            check_time = datetime.datetime.strptime(message.text, '%H:%M')
            time = message.text.split(':')
            hour = time[0]
            minute = time[1]
            add_job(hour, minute)
            lists.add_job = False
            bot.send_message(tlgrm_id, "\xF0\x9F\xA4\x96 Round added!")
        except ValueError:
            bot.send_message(tlgrm_id, "\xF0\x9F\xA4\x96 Incorrect time. Try again")
    elif message.chat.type == "private" and lists.del_job and tlgrm_id == lists.admin \
            and message.text[0].isdigit():
        job_id = message.text[0]
        if int(job_id) in lists.ROUNDS_ID.values():
            try:
                lists.ROUNDS_ID.pop(lists.ROUNDS_ID.keys()[lists.ROUNDS_ID.values().index(int(job_id))])
                job = scheduler.get_job(job_id=str(job_id))
                scheduler.remove_job(job_id=str(job_id))
                lists.del_job = False
                bot.send_message(tlgrm_id, "\xF0\x9F\xA4\x96 Deleted")
            except Exception:
                print Exception
                bot.send_message(tlgrm_id, "Try again")
        else:
            bot.send_message(tlgrm_id, "\xF0\x9F\xA4\x96 Incorrect id. Try again")
    elif chat_id == lists.chat_id and lists.collecting:
        if message.text.startswith('@'):
            words = message.text.split(" ")
            try:
                if db.get_insta_user(tlgrm_id) == "none" and len(words) == 1:
                    insta_user = str(message.text).replace('@', '')
                    db.change_insta_user(insta_user, tlgrm_id)
                    game.collecting_usernames(tlgrm_id, insta_user)
                    bot.send_message(tlgrm_id, 'You`re in for the next round')
            except Exception:
                print Exception
    elif message.from_user.id == lists.admin and lists.collecting:
        tlgrm_id = message.from_user.id
        words = message.text.split(" ")
        try:
            if message.text.startswith('@') and len(words) == 1:
                insta_user = str(message.text).replace('@', '')
                game.collecting_usernames(tlgrm_id, insta_user)
                db.change_insta_user(str(message.text).replace('@', ''), tlgrm_id)
                bot.send_message(tlgrm_id, 'Added to the top of the list!')
        except Exception:
            print Exception
            pass
    elif message.chat.type == "private" and check_user(tlgrm_id):
        if message.text.startswith('@'):
            words = message.text.split(" ")
            try:
                if len(words) == 1:
                    if db.get_insta_user(tlgrm_id) == "none":
                        bot.send_message(tlgrm_id, '\xF0\x9F\x94\xB6 Added!')
                    else:
                        bot.send_message(tlgrm_id, '\xE2\x9C\x8F Your Instagram username has changed!')
                    db.change_insta_user(str(message.text).replace('@', ''), tlgrm_id)
            except Exception:
                print(Exception)
                pass
    else:
        pass



@bot.message_handler(content_types=['new_chat_members'])
def handle_text(message):
    chat_id = message.chat.id
    if chat_id == lists.chat_id:
        members = message.new_chat_members
        for tlgrm_user in members:
            add_user(tlgrm_user.id)
            text = "Hello, %s!\nClick on @RaiseFitnessPlatinumBot and send me your Instagram username to join the game" % tlgrm_user.first_name
            bot.send_message(chat_id, text, parse_mode='Markdown')
            print tlgrm_user.id


@bot.message_handler(content_types=['left_chat_member'])
def handle_text(message):
    chat_id = message.chat.id
    if chat_id == lists.chat_id:
        tlgrm_id = message.left_chat_member.id
        db.del_tlgrm_user(tlgrm_id)


# =============== Scheduler =============== #


def refresh():
    db.refresh()
    db.add_points(395511055, 100)


def weekly_refresh():
    all_points = db.get_all_points()
    for tlgrm_id in all_points.keys():
        if all_points[tlgrm_id] <= 3:
            bot.kick_chat_member(lists.chat_id, tlgrm_id)
    db.refresh()


def add_job(hour, minute):
    job_id = len(lists.ROUNDS_ID) + 1
    time = str(hour) + ":" + str(minute)
    lists.ROUNDS_ID[time] = job_id
    scheduler.add_job(stage_one, 'cron', id=str(job_id), day_of_week='0-6', hour=hour, minute=minute)

# ========================================== #

scheduler.start()

add_job(hour='08',minute='30')
add_job(hour='14',minute='30')
add_job(hour='20',minute='30')


bot.send_message(lists.admin, "\xF0\x9F\xA4\x96 Bot started")
print "Bot started..."

while True:
    try:      
        bot.polling(none_stop=True)
    except Exception as e:
        logger.error(e)
        time.sleep(15)
        continue





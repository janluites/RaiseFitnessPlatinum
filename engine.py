import time
import telebot
import credentials
import game
import lists
import bot
from dbhelper import DBHelper
from collections import OrderedDict

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
        bot.bot.kick_chat_member(lists.chat_id, tlgrm_id)


def get_sorted_list():
    curr_points = {}
    for insta_username in lists.DICT.values():
        print insta_username
        points = db.get_points_by_insta(insta_username)
        print points
        curr_points[insta_username] = points
    print curr_points
    unsort_dict = OrderedDict(sorted(curr_points.items(), key=lambda x: x[1]))
    print unsort_dict
    lists.CURR_POINTS = dict(OrderedDict(reversed(list(unsort_dict.items()))))
    print lists.CURR_POINTS


def stage_one():
    text = "\xE2\x9C\xA8 *Stage 1. Drop time* \xE2\x9C\xA8\n\n" \
           "Type your Instagram username\nlike this *@username*."
    bot.bot.send_message(lists.chat_id, text, parse_mode='Markdown')
    lists.collecting = True
    lists.game_active = True
    time.sleep(15)
    stage_two()


def stage_two():
    lists.collecting = False
    game.save_results()
    get_sorted_list()
    text = "\xE2\x9C\xA8 *Stage 2. Like and comment* \xE2\x9C\xA8\n\n"
    for insta_username in lists.CURR_POINTS.keys():
        text += '_@%s_\n' % insta_username
    bot.bot.send_message(lists.chat_id, text, parse_mode='Markdown')
    print lists.DICT
    time.sleep(5)
    text = "\xE2\x9C\xA8 *Checking results...* \xE2\x9C\xA8\n\n"
    bot.bot.send_message(lists.chat_id, text, parse_mode='Markdown')
    results()


def results():
    if game.check_results():
        text = "\xE2\x9D\x8C *Round completed!* \xE2\x9D\x8C"
        bot.bot.send_message(lists.chat_id, text, parse_mode='Markdown')
        for tlgrm_id in lists.POINTS.keys():
            if lists.POINTS[tlgrm_id] == 1:
                db.add_points(tlgrm_id, 1)
                bot.bot.send_message(tlgrm_id, '\xF0\x9F\x94\xB5 You have completed this round!')
            else:
                warning(tlgrm_id)
                bot.bot.send_message(tlgrm_id, '\xF0\x9F\x94\xB4 Warning! You don`t completed this round')
        lists.POINTS = {}
        lists.game_active = False
    else:
        bot.bot.send_message(lists.chat_id, '\xF0\x9F\x98\x9E Sorry, I need more users to play this game')


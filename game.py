# -*- coding: utf-8 -*-

import instagram_engine
import lists


def collecting_usernames(tlgrm_id, insta_user):
    lists.UNFORM_DICT[tlgrm_id] = insta_user


def save_results():
    lists.DICT = dict(lists.UNFORM_DICT)
    lists.UNFORM_DICT = {}


def check_results():
    try:
        for tlgrm_id in lists.DICT.keys():
            lists.POINTS[tlgrm_id] = 0
        result_dict = dict(zip(lists.DICT.keys(), lists.ID_LIST))
        print result_dict
        for tele_id in result_dict.keys():
            for insta_id in result_dict.values():
                if insta_id == result_dict[tele_id]:
                    pass
                else:
                    insta_user = result_dict[tele_id]
                    shortcode = instagram_engine.get_shortcode(insta_id)
                    LIKES_LIST = instagram_engine.get_likes(shortcode)
                    COMMENTS_LIST = instagram_engine.get_comments(shortcode)
                    if LIKES_LIST is None or COMMENTS_LIST is None:
                        lists.POINTS[tele_id] += 1
                    else:
                        if points(insta_user, tele_id, LIKES_LIST, COMMENTS_LIST) is False:
                            break
        print "All points: ", lists.POINTS
        return True
    except Exception as e:
        print e
        return False


def points(insta_user, tele_user, likes, comments):
    if str(insta_user) in likes and str(insta_user) in comments:
        lists.POINTS[tele_user] += 1
        print "Points: ", lists.POINTS[tele_user]
        return True
    else:
        lists.POINTS[tele_user] = 0
        print "Points: ", lists.POINTS[tele_user]
        return False


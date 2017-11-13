# -*- coding: utf-8 -*-

import sqlite3


class DBHelper:
    
    def __init__(self, dbname="main.sqlite"):
        self.dbname = dbname
        self.conn = sqlite3.connect(dbname, check_same_thread=False)
        self.c = self.conn.cursor()

    def setup(self):
        stmt = """CREATE TABLE IF NOT EXISTS data (tlgrm_id INTEGER NOT NULL,
                                                   insta_user DEFAULT none,
                                                   points DEFAULT 0,                                                  
                                                   warnings DEFAULT 0)"""
        self.c.execute(stmt)
        self.conn.commit()

    def add_tlgrm_user(self, tlgrm_id):
        self.c.execute("INSERT INTO data (tlgrm_id) VALUES (?)", (tlgrm_id, ))
        self.conn.commit()

    def get_tlgrm_user(self, tlgrm_id):
        self.c.execute("SELECT tlgrm_id FROM data WHERE tlgrm_id=?", (tlgrm_id, ))
        user = self.c.fetchone()
        if user is not None:
            return user[0]
        else:
            return None

    def del_tlgrm_user(self, tlgrm_id):
        self.c.execute("DELETE FROM data WHERE tlgrm_id=?", (tlgrm_id, ))
        self.conn.commit()

    def get_insta_user(self, tlgrm_id):
        self.c.execute("SELECT insta_user FROM data WHERE tlgrm_id=?", (tlgrm_id, ))
        insta_user = self.c.fetchone()
        return str(insta_user[0])

    def change_insta_user(self, insta_id, tlgrm_id):
        self.c.execute("UPDATE data SET insta_user=? WHERE tlgrm_id=? ", (insta_id, tlgrm_id))
        self.conn.commit()

    def add_points(self, tlgrm_id, user_points):
        points = self.get_points_by_tele(tlgrm_id)
        result = points + user_points
        self.c.execute("UPDATE data SET points=? WHERE tlgrm_id=?", (result, tlgrm_id))
        self.conn.commit()

    def get_points_by_insta(self, insta_username):
        self.c.execute("SELECT points FROM data WHERE insta_user=?", (insta_username, ))
        points = self.c.fetchone()
        return int(points[0])

    def get_points_by_tele(self, tlgrm_id):
        self.c.execute("SELECT points FROM data WHERE tlgrm_id=?", (tlgrm_id, ))
        points = self.c.fetchone()
        return int(points[0])

    def get_all_points(self):
        all_points = {}
        for user in self.c.execute("SELECT tlgrm_id, points  FROM data"):
            all_points[user[0]] = user[1]
        return all_points

    def add_warning(self, tlgrm_id):
        warnings = self.get_warnings(tlgrm_id)
        warnings += 1
        self.c.execute("UPDATE data SET warnings=? WHERE tlgrm_id=?", (warnings, tlgrm_id))
        self.conn.commit()

    def get_warnings(self, tlgrm_id):
        self.c.execute("SELECT warnings FROM data WHERE tlgrm_id=?", (tlgrm_id, ))
        points = self.c.fetchone()
        return int(points[0])

    def refresh(self):
        points = 0
        warnings = 0
        self.c.execute("UPDATE data SET points=?, warnings=?", (points, warnings))
        self.conn.commit()


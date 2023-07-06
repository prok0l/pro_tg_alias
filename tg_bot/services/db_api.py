import sqlite3
import os


class DBApi:
    def __init__(self, path):
        self.path = path
        self.global_init()

    def connect(self, text_for_execute: str, fetchall: bool = False,
                params: tuple = ()):
        with sqlite3.connect(self.path) as conn:
            conn.cursor()
            if fetchall:
                return conn.execute(text_for_execute, params).fetchall()
            else:
                conn.execute(text_for_execute, params)
                conn.commit()

    def global_init(self):
        print(
            "Connecting to the database at " + '"' + self.path + '"')
        if not os.path.exists(self.path):
            with open(self.path):
                pass
            # TODO прописать команды создания таблиц

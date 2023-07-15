import sqlite3
import os

from tg_bot.services.consts import DeckTypes, DeckTypesList


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
            with open(self.path, "w+"):
                pass
            self.connect(text_for_execute="""
                         CREATE TABLE IF NOT EXISTS `users` (
                            `tg_id` INTEGER PRIMARY KEY,
                            `username` TEXT NOT NULL,
                            `limit` INTEGER NOT NULL DEFAULT 1
                        );""")
            self.connect(text_for_execute="""
                         CREATE TABLE IF NOT EXISTS `deck_type` (
                            `id` INTEGER PRIMARY KEY AUTOINCREMENT,
                            `name` TEXT NOT NULL,
                            `is_public` BOOLEAN NOT NULL
                        );
                         """)
            self.connect(text_for_execute="""
                         CREATE TABLE IF NOT EXISTS `decks` (
                            `id` INTEGER PRIMARY KEY AUTOINCREMENT,
                            `name` TEXT NOT NULL UNIQUE,
                            `type` INTEGER NOT NULL,
                            `owner` INTEGER,
                            `path` TEXT,
                            FOREIGN KEY (`owner`) REFERENCES `users`(`tg_id`),
                            FOREIGN KEY (`type`) REFERENCES `deck_type`(`id`)
                        );
                         """)
            self.connect(text_for_execute="""
                         CREATE TABLE IF NOT EXISTS `decks_users` (
                        `id` INTEGER PRIMARY KEY AUTOINCREMENT,
                        `id_user` INTEGER NOT NULL,
                        `id_deck` INTEGER NOT NULL,
                        FOREIGN KEY (`id_user`) REFERENCES `users` (`tg_id`),
                        FOREIGN KEY (`id_deck`) REFERENCES `decks` (`id`)
                    );
                         """)
            self.connect(text_for_execute="""
                         CREATE TABLE IF NOT EXISTS `settings_user` (
                        `id_user` INTEGER NOT NULL UNIQUE,
                        `duration` INTEGER NOT NULL DEFAULT '60',
                        `now_deck` INTEGER NOT NULL,
                        FOREIGN KEY (`id_user`) REFERENCES `users` (`tg_id`),
                        FOREIGN KEY (`now_deck`) REFERENCES `decks_users`(`id`)
                    );

                         """)
            for par in DeckTypesList.Types.value:
                self.connect(text_for_execute=
                             """INSERT INTO deck_type(name, is_public)
                            VALUES(?, ?)""",
                             params=par)
            pub_type_id = self.connect(text_for_execute=
                                       "SELECT id FROM deck_type WHERE name=?",
                                       params=(DeckTypes.Public.value, ),
                                       fetchall=True)[0][0]
            decks = [("Alias party", pub_type_id, "1.txt"),
                     ("Alias дамы против джентельменов (муж. версия)",
                      pub_type_id, "2.txt"),
                     ("Alias дамы против джентельменов (жен. версия)",
                      pub_type_id, "3.txt")]
            for deck in decks:
                self.connect(text_for_execute="""
                            INSERT INTO decks(name, type, path)
                            VALUES(?, ?, ?)""",
                                              params=deck)

    def create_user(self, tg_id, username):
        if self.connect(text_for_execute="""
        SELECT * FROM users WHERE tg_id=?;
        """, params=(tg_id, ), fetchall=True):
            return None
        self.connect(text_for_execute="""
        INSERT INTO users(tg_id, username) VALUES(?, ?)""",
                     params=(tg_id, username, ))
        decks = self.connect("""SELECT id FROM decks ORDER BY id LIMIT 1""",
                             fetchall=True)[0][0]
        now_deck = self.connect(text_for_execute=
                                """
        INSERT INTO decks_users(id_user, id_deck) VALUES(?, ?) RETURNING id""",
                                params=(tg_id, decks), fetchall=True)[0][0]
        self.connect(text_for_execute="""
        INSERT INTO settings_user(id_user, now_deck)
         VALUES(?, ?)""", params=(tg_id, now_deck))

    def user_info(self, tg_id):
        dur, now_deck_link = self.connect(text_for_execute=
                                          """
        SELECT duration, now_deck FROM settings_user WHERE id_user=?""",
                                          params=(tg_id, ), fetchall=True)[0]
        now_deck_id = self.connect(text_for_execute="""
        SELECT id_deck FROM decks_users WHERE id=?""",
                                   params=(now_deck_link, ),
                                   fetchall=True)[0]
        now_deck_path = self.connect("""SELECT path FROM decks WHERE id=?""",
                                     params=now_deck_id, fetchall=True)[0][0]
        return dur, now_deck_path

    def change_duration(self, tg_id, new_duration):
        self.connect(text_for_execute="""
        UPDATE settings_user SET duration=? WHERE id_user=?""",
                     params=(new_duration, tg_id, ))

    def change_deck(self, tg_id, deck_link):
        if not self.connect("""SELECT * FROM decks_users WHERE id=?
         AND id_user=?""",
                            params=(deck_link, tg_id), fetchall=True):
            return None
        self.connect(text_for_execute="""
                UPDATE settings_user SET now_deck=? WHERE id_user=?""",
                     params=(deck_link, tg_id,))

    def decks_by_tg_id(self, tg_id):
        decks_id = self.connect("""SELECT id, id_deck FROM decks_users
         WHERE id_user=?""", params=(tg_id, ), fetchall=True)
        decks = []
        for deck_id in decks_id:
            deck_name = self.connect("""SELECT name FROM decks WHERE id=?""",
                                     params=(deck_id[1], ),
                                     fetchall=True)[0][0]
            decks.append((deck_id[0], deck_name))
        return decks

    def is_max_decks(self, tg_id):
        limit = self.connect(text_for_execute=
                             "SELECT `limit` FROM users WHERE tg_id=?;",
                             params=(tg_id, ), fetchall=True)
        if not limit:
            return True
        else:
            limit = limit[0][0]
        if limit == -1:
            return False
        count = self.connect("SELECT COUNT (*) FROM decks WHERE owner=?;",
                             params=(tg_id, ), fetchall=True)[0][0]
        if count >= limit:
            return True
        return False

    def new_deck(self, tg_id, name, path):
        if self.is_max_decks(tg_id=tg_id):
            return None
        pub_type_id = self.connect(text_for_execute=
                                   "SELECT id FROM deck_type WHERE name=?",
                                   params=(DeckTypes.Private.value,),
                                   fetchall=True)[0][0]
        deck_id = self.connect(text_for_execute=
                               "INSERT INTO decks(name, type, owner, path)"
                               "VALUES(?, ?, ?, ?) RETURNING id;",
                               params=(name, pub_type_id, tg_id, path, ),
                               fetchall=True)[0][0]
        self.add_deck(tg_id=tg_id, deck_id=deck_id)
        return deck_id

    def add_deck(self, tg_id, deck_id):
        if self.connect(text_for_execute=
                        "SELECT * FROM decks_users WHERE id_user=? AND "
                        "id_deck=?", params=(tg_id, deck_id, ),
                        fetchall=True):
            return None

        link_id = self.connect(text_for_execute=
                               "INSERT INTO decks_users(id_user, id_deck)"
                               "VALUES(?, ?) RETURNING id;",
                               params=(tg_id, deck_id, ), fetchall=True)[0][0]
        self.change_deck(tg_id=tg_id, deck_link=link_id)
        return link_id

    def check_deck_name(self, deck_name):
        if self.connect(text_for_execute=
                     "SELECT * FROM decks WHERE name=?",
                     params=(deck_name, ),
                     fetchall=True):
            return False
        return True

    def check_deck_id(self, deck_id):
        if self.connect(text_for_execute=
                        "SELECT * FROM decks WHERE id=?",
                        params=(deck_id, ),
                        fetchall=True):
            return True
        return False


if __name__ == '__main__':
    obj = DBApi("../../systemd/2.db")

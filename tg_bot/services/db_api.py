import sqlite3
import os

from tg_bot.services.consts import DeckTypes, DeckTypesList, LimitText
from tg_bot.services.file_filter import file_filter
from tg_bot.services.consts import Path


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
        """
        функция глобальной инициализации (создание всех таблиц и т.д.)
        :return:
        """
        print(
            "Connecting to the database at " + '"' + self.path + '"')
        if not os.path.exists(self.path):
            with open(self.path, "w+"):
                pass
            self.connect(text_for_execute="""
                         CREATE TABLE IF NOT EXISTS `users` (
                            `tg_id` INTEGER PRIMARY KEY,
                            `username` TEXT,
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
                            `num_words` INTEGER,
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
                        `now_deck` INTEGER,
                        FOREIGN KEY (`id_user`) REFERENCES `users` (`tg_id`),
                        FOREIGN KEY (`now_deck`) REFERENCES `decks_users`(`id`)
                    );

                         """)
            for par in DeckTypesList.Types.value:
                self.connect(text_for_execute="""INSERT INTO
                 deck_type(name, is_public) VALUES(?, ?)""",
                             params=par)
            pub_type_id = self.connect(text_for_execute="SELECT id "
                                                        "FROM deck_type "
                                                        "WHERE name=?",
                                       params=(DeckTypes.PUBLIC.value,),
                                       fetchall=True)[0][0]
            decks = [("Alias party", pub_type_id, "1.txt", 1991),
                     ("Alias дамы против джентельменов (муж. версия)",
                      pub_type_id, "2.txt", 1200),
                     ("Alias дамы против джентельменов (жен. версия)",
                      pub_type_id, "3.txt", 1180)]
            for deck in decks:
                self.connect(text_for_execute="""
                            INSERT INTO decks(name, type, path, num_words)
                            VALUES(?, ?, ?)""",
                             params=deck)

    def create_user(self, tg_id, username):
        """
        функция создания юзера (триггер handler start.py)
        :param tg_id:
        :param username:
        :return:
        """
        if self.connect(text_for_execute="""
        SELECT * FROM users WHERE tg_id=?;
        """, params=(tg_id,), fetchall=True):
            return None
        self.connect(text_for_execute="""
        INSERT INTO users(tg_id, username) VALUES(?, ?)""",
                     params=(tg_id, username,))
        decks = self.connect("""SELECT id FROM decks ORDER BY id LIMIT 1""",
                             fetchall=True)[0][0]
        now_deck = self.connect(text_for_execute="""
        INSERT INTO decks_users(id_user, id_deck) VALUES(?, ?) RETURNING id""",
                                params=(tg_id, decks), fetchall=True)[0][0]
        self.connect(text_for_execute="""
        INSERT INTO settings_user(id_user, now_deck)
         VALUES(?, ?)""", params=(tg_id, now_deck))

    def user_info(self, tg_id):
        """
        функция возврата времени раунда и текущей колоды
        :param tg_id:
        :return:
        """
        dur, now_deck_path = self.connect(text_for_execute="""
        SELECT duration, now_deck FROM settings_user WHERE id_user=?""",
                                          params=(tg_id,), fetchall=True)[0]
        if now_deck_path:
            now_deck_id = self.connect(text_for_execute="""
            SELECT id_deck FROM decks_users WHERE id=?""",
                                       params=(now_deck_path,),
                                       fetchall=True)[0]
            now_deck_path = self.connect("""SELECT path FROM decks
             WHERE id=?""", params=now_deck_id, fetchall=True)[0][0]

        return dur, now_deck_path

    def change_duration(self, tg_id, new_duration):
        """
        смена длительности раунда
        :param tg_id:
        :param new_duration:
        :return:
        """
        self.connect(text_for_execute="""
        UPDATE settings_user SET duration=? WHERE id_user=?""",
                     params=(new_duration, tg_id,))

    def change_deck(self, tg_id, deck_link):
        """
        функция смены текущей выбранной колоды
        :param tg_id:
        :param deck_link: ссылка на id таблицы decks_users
        :return:
        """
        # if not self.connect("""SELECT * FROM decks_users WHERE id=?
        #  AND id_user=?""",
        #                     params=(deck_link, tg_id), fetchall=True):
        #     return None
        self.connect(text_for_execute="""
                UPDATE settings_user SET now_deck=? WHERE id_user=?""",
                     params=(deck_link, tg_id,))

    def decks_by_tg_id(self, tg_id):
        """
        функция для получения линкованных колод с юзером
        :param tg_id:
        :return:
        """
        now_deck = self.connect(text_for_execute="""
        SELECT now_deck FROM settings_user WHERE id_user=?""",
                                params=(tg_id,), fetchall=True)[0][0]

        decks_id = self.connect("""SELECT id, id_deck FROM decks_users
         WHERE id_user=?""", params=(tg_id,), fetchall=True)
        decks = []
        for deck_id in decks_id:
            deck_info = self.connect("""SELECT name, num_words
             FROM decks WHERE id=?""",
                                     params=(deck_id[1],),
                                     fetchall=True)[0]
            decks.append((deck_id[0], deck_info[0], deck_info[1]))
        return decks, now_deck

    def is_max_decks(self, tg_id):
        """
        функция проверки лимита количества созданных колод
        :param tg_id:
        :return:
        """
        limit = self.connect(text_for_execute="SELECT `limit` FROM"
                                              " users WHERE tg_id=?;",
                             params=(tg_id,), fetchall=True)
        if not limit:
            return True
        else:
            limit = limit[0][0]
        if limit == -1:
            return False
        count = self.connect("SELECT COUNT (*) FROM decks WHERE owner=?;",
                             params=(tg_id,), fetchall=True)[0][0]
        if count >= limit:
            return True
        return False

    def new_deck(self, tg_id, name, path, num_words):
        """
        функция создания новой колоды
        :param tg_id:
        :param name:
        :param path:
        :param num_words:
        :return:
        """
        if self.is_max_decks(tg_id=tg_id):
            return None
        pub_type_id = self.connect(text_for_execute="SELECT id FROM"
                                                    " deck_type WHERE name=?",
                                   params=(DeckTypes.PRIVATE.value,),
                                   fetchall=True)[0][0]
        deck_id = self.connect(text_for_execute="INSERT INTO decks("
                                                "name, type, owner, path,"
                                                " num_words) "
                                                "VALUES(?, ?, ?, ?, ?)"
                                                " RETURNING id;",
                               params=(name, pub_type_id, tg_id, path,
                                       num_words),
                               fetchall=True)[0][0]
        self.add_deck(tg_id=tg_id, deck_id=deck_id)
        return deck_id

    def add_deck(self, tg_id, deck_id):
        """
        функция добавления колоды к списку колод пользователя (линковка)
        также выставляет новодобавленную колоду в текущую
        :param tg_id:
        :param deck_id:
        :return:
        """
        if self.connect(text_for_execute="SELECT * FROM decks_users"
                                         " WHERE id_user=? AND "
                                         "id_deck=?",
                        params=(tg_id, deck_id,),
                        fetchall=True):
            return None

        link_id = self.connect(text_for_execute="INSERT INTO"
                                                " decks_users(id_user, id_deck)"
                                                " VALUES(?, ?) RETURNING id;",
                               params=(tg_id, deck_id,), fetchall=True)[0][0]
        self.change_deck(tg_id=tg_id, deck_link=link_id)
        return link_id

    def check_deck_name(self, deck_name):
        """
        функция проверки уникальности названия колоды
        :param deck_name:
        :return:
        """
        if self.connect(text_for_execute="SELECT * FROM decks WHERE name=?",
                        params=(deck_name,),
                        fetchall=True):
            return False
        return True

    def check_deck_id(self, deck_id):
        """
        функция проверки существования колоды по его id
        :param deck_id:
        :return:
        """
        if self.connect(text_for_execute="SELECT * FROM decks WHERE id=?",
                        params=(deck_id,),
                        fetchall=True):
            return True
        return False

    def deck_info(self, tg_id, deck_id):
        """
        функция проверки колоды перед линковкой
        возвращает None, если колода уже была добавлена
        возвращает название колоды и количество слов
        :param tg_id:
        :param deck_id:
        :return:
        """
        if self.connect(text_for_execute="SELECT * FROM decks_users"
                                         " WHERE id_user=? AND id_deck=?",
                        params=(tg_id, deck_id,),
                        fetchall=True):
            return None
        name, num_words = self.connect(text_for_execute="SELECT name, num_words"
                                                        " FROM"
                                                        " decks WHERE id=?",
                                       params=(deck_id,), fetchall=True)[0]
        return name, num_words

    def del_deck_link(self, tg_id, deck_link):
        """
        удаляет линковку колоды с юзером
        :param tg_id:
        :param deck_link:
        :return:
        """
        if self.connect("SELECT * FROM settings_user WHERE id_user=? AND "
                        "now_deck=?",
                        params=(tg_id, deck_link,), fetchall=True):
            self.connect(text_for_execute="""
            UPDATE settings_user SET now_deck=? WHERE id_user=?""",
                         params=(None, tg_id,))
        self.connect("DELETE FROM decks_users WHERE id=?",
                     params=(deck_link,))

    def decks_shop(self, tg_id):
        """
        функция получения одобренных колод (Public)
        также возвращает True если колода уже есть у пользователя
        :param tg_id:
        :return:
        """
        pub_id = self.connect("SELECT id FROM deck_type "
                              "WHERE is_public", fetchall=True)[0][0]
        decks = self.connect("SELECT id, name, num_words FROM decks "
                             "WHERE type=?",
                             params=(pub_id,), fetchall=True)
        for i in range(len(decks)):
            deck_id, _, _ = decks[i]
            decks[i] += (bool(self.connect("SELECT * FROM decks_users "
                                           "WHERE id_user=? AND id_deck=?",
                                           params=(tg_id, deck_id),
                                           fetchall=True)),)
        return decks

    def refactor_deck(self, deck_id):
        """
        функция смены статуса колоды на ожидание (On Moderation),
        если до этого она была (Public), триггер rename_deck,
        change_file_in_deck
        :param deck_id:
        :return:
        """
        pub_id = self.connect("SELECT id FROM deck_type WHERE is_public",
                              fetchall=True)[0][0]
        if self.connect("SELECT type FROM decks WHERE id=?",
                        params=(deck_id,), fetchall=True)[0][0] == pub_id:
            mod_id = self.connect("SELECT id FROM deck_type WHERE name=?",
                                  params=(DeckTypes.MODERATION.value,),
                                  fetchall=True)[0][0]
            self.connect("UPDATE decks SET type=? WHERE id=?",
                         params=(mod_id, deck_id))

    def rename_deck(self, deck_id, new_name):
        """
        функция переименования колоды
        :param deck_id:
        :param new_name:
        :return:
        """
        if not self.check_deck_name(deck_name=new_name):
            return False
        self.refactor_deck(deck_id=deck_id)
        self.connect("UPDATE decks SET name=? WHERE id=?",
                     params=(new_name, deck_id,))
        return True

    def change_file_in_deck(self, deck_id, new_path, num_words):
        """
        функция смены загрузочного файла колоды
        :param deck_id:
        :param new_path:
        :param num_words:
        :return:
        """
        self.refactor_deck(deck_id=deck_id)
        self.connect("UPDATE decks SET path=?, num_words=? WHERE id=?",
                     params=(new_path, num_words, deck_id,))

    def change_type_deck(self, deck_id, new_type):
        """
        функция смены статуса колоды
        :param deck_id:
        :param new_type:
        :return:
        """
        type_id = self.connect("SELECT id FROM deck_type WHERE name=?",
                               params=(new_type,),
                               fetchall=True)[0][0]
        self.connect("UPDATE decks SET type=? WHERE id=?",
                     params=(type_id, deck_id))

    def change_num_words(self, deck_id, new_num):
        """
        функция изменения количества слов в колоде
        :param deck_id:
        :param new_num:
        :return:
        """
        self.connect("UPDATE `decks` SET `num_words`=? WHERE `id`=?",
                     params=(new_num, deck_id,))

    def decks_by_owner(self, tg_id):
        """
        функция возврата колод, созданных (tg_id)
        :param tg_id:
        :return:
        """
        decks_lst = self.connect("SELECT id, name, type, `num_words` FROM"
                                 " decks WHERE owner=?",
                                 params=(tg_id,),
                                 fetchall=True)
        decks = []
        for deck in decks_lst:
            type_deck = self.connect("SELECT name FROM deck_type WHERE id=?",
                                     params=(deck[2],), fetchall=True)[0][0]
            decks.append([deck[0], deck[1], type_deck, deck[3]])
        return decks

    def del_deck(self, deck_id):
        """
        удалить колоду (триггер list_decks)
        :param deck_id:
        :return:
        """
        users = self.connect(text_for_execute="""
        SELECT id_user, id FROM decks_users WHERE id_deck=?""",
                             params=(deck_id,), fetchall=True)
        for user in users:
            self.del_deck_link(tg_id=user[0],
                               deck_link=user[1])
        self.connect(text_for_execute="""
        DELETE FROM decks WHERE id=?""",
                     params=(deck_id,))

    def my_account(self, tg_id):
        """
        функция для обработки хэндлера my_account
        :param tg_id:
        :return:
        """
        dur, _ = self.user_info(tg_id=tg_id)
        deck_links = self.decks_by_tg_id(tg_id=tg_id)
        deck_owner = self.decks_by_owner(tg_id=tg_id)
        limit = self.connect(text_for_execute="SELECT `limit` FROM"
                                              " users WHERE tg_id=?;",
                             params=(tg_id,), fetchall=True)
        if not limit:
            limit = 0
        else:
            limit = limit[0][0]
        if limit == -1:
            limit = LimitText.UNLIMIT.value
        count = self.connect("SELECT COUNT (*) FROM decks WHERE owner=?;",
                             params=(tg_id,), fetchall=True)[0][0]
        return dur, deck_links, deck_owner, limit, count

    def add_num_words_column(self):
        """
        системная функция необходимая, для создания поля количество слов
        :return:
        """
        self.connect(text_for_execute="ALTER TABLE decks ADD"
                                      " `num_words` INTEGER")
        decks = self.connect("SELECT `id`, `path` FROM decks",
                             fetchall=True)
        for deck_id, deck_path in decks:
            count_words = file_filter("../../" + Path.DECKS.value + deck_path)
            self.connect("UPDATE `decks` SET `num_words`=? WHERE `id`=?",
                         params=(count_words, deck_id, ))

    def users(self):
        """
        функция для обработки хендлера users (выдача всех юзеров)
        :return:
        """
        return self.connect("SELECT * FROM users;", fetchall=True)

    def check_user_in_db(self, tg_id):
        """
        функция проверки, есть ли юзер в бд
        :param tg_id:
        :return:
        """
        return self.connect("SELECT * FROM users WHERE tg_id=?",
                            params=(tg_id, ), fetchall=True)

    def change_limit(self, tg_id, new_limit):
        """
        функция смены лимита у юзера
        :param tg_id:
        :param new_limit:
        :return:
        """
        self.connect("UPDATE users SET `limit`=? WHERE tg_id=?",
                     params=(new_limit, tg_id))

    def moderation(self):
        """
        функция для модерации колод
        :return:
        """
        mod_id = self.connect("SELECT id FROM deck_type WHERE name=?",
                              params=(DeckTypes.MODERATION.value, ),
                              fetchall=True)[0][0]
        decks = self.connect("SELECT id, name, owner, path, num_words"
                             " FROM decks "
                             "WHERE type=?",
                             params=(mod_id, ), fetchall=True)
        decks_with_username = []
        for (deck_id, name, tg_id, path, num_words) in decks:
            username = self.connect("SELECT username FROM users WHERE tg_id=?",
                                    params=(tg_id, ), fetchall=True)[0][0]
            decks_with_username.append([deck_id, name, username,
                                        path, num_words])
        return decks_with_username


if __name__ == '__main__':
    obj = DBApi("../../systemd/1.db")
    obj.add_num_words_column()

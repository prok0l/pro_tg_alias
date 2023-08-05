# Telegram bot для игры в Alias, с возможностью создания собственной колоды

### [BOT_URL](https://t.me/alias_tgbot)

---
### Благодарность за помощь в разработке:
 - [SilverSheldon](https://github.com/SilverSheldon)
 - [ShadowM4rsh](https://github.com/ShadowM4rsh)
 - [Vera152022](https://github.com/Vera152022)
 - [nekitleo](https://github.com/nekitleo)

---
### Cтарт проекта:
- создание .env файла
    ```dotenv
    BOT_TOKEN=
    ADMINS=
    USE_REDIS=False
   ```
- запуск контейнера
    ```shell
    docker-compose up
    ```
---
#### Список команд:  
- [/start](https://t.me/alias_tgbot) - старт бота  
- [/help](https://t.me/alias_tgbot) - список команд  
- [/new_game](https://t.me/alias_tgbot) - запустить игру  
- [/stop_game](https://t.me/alias_tgbot) - остановить игру  
- [/add_deck](https://t.me/alias_tgbot) - добавить колоду через id  
- [/duration](https://t.me/alias_tgbot) - длительность раунда  
- [/my_decks](https://t.me/alias_tgbot) - список колод  
- [/new_deck](https://t.me/alias_tgbot) - создать свою колоду  
- [/decks_shop](https://t.me/alias_tgbot) - магазин колод  
- [/list_decks](https://t.me/alias_tgbot) - колоды созданные мной  
- [/my_account](https://t.me/alias_tgbot) - информация об аккаунте  
- [/cancel](https://t.me/alias_tgbot) - отменить операцию  
- [/users](https://t.me/alias_tgbot) - список пользователей  
- [/change_limit](https://t.me/alias_tgbot) - смена лимита пользователя по его id  
- [/moderation](https://t.me/alias_tgbot) - модерация колод
---
### License

[(The MIT License)](LICENSE)
## **func** -- "add_deck"
функция добавления колоды к списку колод пользователя (линковка) также выставляет новодобавленную колоду в текущую   
:param tg_id:  
:param deck_id:  
:return:

## **func** -- "change_deck"
функция смены текущей выбранной колоды   
:param tg_id:  
:param deck_link: ссылка на id таблицы decks_users  
:return:

## **func** -- "change_duration"
смена длительности раунда   
:param tg_id:  
:param new_duration:  
:return:

## **func** -- "change_file_in_deck"
функция смены загрузочного файла колоды   
:param deck_id:  
:param new_path:  
:return:

## **func** -- "change_limit"
функция смены лимита у юзера   
:param tg_id:  
:param new_limit:  
:return:

## **func** -- "change_type_deck"
функция смены статуса колоды   
:param deck_id:  
:param new_type:  
:return:

## **func** -- "check_deck_id"
функция проверки существования колоды по его id   
:param deck_id:  
:return:

## **func** -- "check_deck_name"
функция проверки уникальности названия колоды   
:param deck_name:  
:return:

## **func** -- "check_user_in_db"
функция проверки, есть ли юзер в бд   
:param tg_id:  
:return:

## **func** -- "create_user"
функция создания юзера (триггер handler start.py)   
:param tg_id:  
:param username:  
:return:

## **func** -- "deck_info"
функция проверки колоды перед линковкой возвращает None, если колода уже была добавлена возвращает название колоды   
:param tg_id:  
:param deck_id:  
:return:

## **func** -- "decks_by_owner"
функция возврата колод, созданных (tg_id)   
:param tg_id:  
:return:

## **func** -- "decks_by_tg_id"
функция для получения линкованных колод с юзером   
:param tg_id:  
:return:

## **func** -- "decks_shop"
функция получения одобренных колод (Public) также возвращает True если колода уже есть у пользователя   
:param tg_id:  
:return:

## **func** -- "del_deck"
удалить колоду (триггер list_decks)   
:param deck_id:  
:return:

## **func** -- "del_deck_link"
удаляет линковку колоды с юзером   
:param tg_id:  
:param deck_link:  
:return:

## **func** -- "global_init"
функция глобальной инициализации (создание всех таблиц и т.д.)   
:return:

## **func** -- "is_max_decks"
функция проверки лимита количества созданных колод   
:param tg_id:  
:return:

## **func** -- "moderation"
функция для модерации колод   
:return:

## **func** -- "my_account"
функция для обработки хэндлера my_account   
:param tg_id:  
:return:

## **func** -- "new_deck"
функция создания новой колоды   
:param tg_id:  
:param name:  
:param path:  
:return:

## **func** -- "refactor_deck"
функция смены статуса колоды на ожидание (On Moderation), если до этого она была (Public), триггер rename_deck, change_file_in_deck   
:param deck_id:  
:return:

## **func** -- "rename_deck"
функция переименования колоды   
:param deck_id:  
:param new_name:  
:return:

## **func** -- "user_info"
функция возврата времени раунда и текущей колоды   
:param tg_id:  
:return:

## **func** -- "users"
функция для обработки хендлера users (выдача всех юзеров)   
:return:


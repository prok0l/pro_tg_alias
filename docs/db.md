# **Database Documentation.** 

## **TABLE** -- "users"
field `tg_id` - telegram user id    Type:`integer`   
field `username` - telegram username    Type:`text`   
field `limit` - deck limit   Type:`integer`   


## **TABLE** -- "deck_type"
field `id` - id type (status of deck)       Type:`integer`   
field `name` - status name      Type:`text`   
field `is_public` - is there a global placement right    Type:`boolean`   


## **TABLE** -- "decks"
field `id` - deck id     Type:`integer`   
field `name` - deck name     Type:`text`   
field `type` - deck status (fk: deck_type.id)   Type:`integer`   
field `owner` - deck owner (fk: users.tg_id)     Type:`integer`   
field `path` - deck file path    Type:`text`   


## **TABLE** -- "decks_users"
field `id` - link id     Type:`integer`   
field `id_user` - user id (fk: users.tg_id)  Type:`integer`   
field `id_deck` - deck id (fk: decks.id)     Type:`integer`   


## **TABLE** -- "settings_user"
field `id_user` - telegram user id (fk: users.tg_id)     Type:`integer`   
field `duration` - round duration    Type:`integer`   
field `now_deck` - current deck (fk: decks_users.id) Type:`integer`   



from enum import Enum


class Path(str, Enum):
    decks = "systemd/decks/"


class DeckTypes(str, Enum):
    Public = "Public"
    Private = "Private"
    Moderation = "On moderation"


class DeckTypesList(list, Enum):
    Types = [(DeckTypes.Public, True),
             (DeckTypes.Private, False),
             (DeckTypes.Moderation, False)]


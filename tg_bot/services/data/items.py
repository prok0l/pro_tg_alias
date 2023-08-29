from aiogram.types import LabeledPrice

from tg_bot.services.data.item import Item

One_limit = Item(
    title="Увеличить лимит на 1 ед.",
    description="Увеличить количество создаваемых колод",
    currency="rub",
    prices=[
        LabeledPrice(label="Увеличить лимит на 1 ед.",
                     amount=100_00)
    ],
    start_parameter="plus_one_limit_start"
)

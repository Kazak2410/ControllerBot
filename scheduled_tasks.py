from datetime import datetime, timedelta
from aiogram import Bot


async def send_message_cron(bot: Bot, products):
    products_for_sale = []
    for product in products:
        shelf_life = abs(((datetime.now()) - datetime.strptime(product[2], "%d.%m.%y")).days)
        if shelf_life <= 4:
            products_for_sale.append(product)
    products_for_sale = "\n".join(str(product) for product in products_for_sale)
    message = f"Эти товары желательно продать:\n{products_for_sale}"
    await bot.send_message(-945893857, message)

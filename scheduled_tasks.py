from datetime import datetime, timedelta
from aiogram import Bot


async def send_message_cron(bot: Bot, products):
    products_for_sale = []
    for product in products:
        shelf_life = datetime.strptime(product[1], "%d.%m.%y") - timedelta(days=4)
        if shelf_life.strftime("%d.%m.%y") == datetime.now().strftime("%d.%m.%y"):
            products_for_sale.append(product)
    products_for_sale = "\n".join(product for product in products_for_sale)
    message = f"Эти товары желательно продать:\n{products_for_sale}"
    await bot.send_message(-945893857, message)

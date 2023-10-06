from datetime import datetime, timedelta
from aiogram import Bot


async def send_message_cron(bot: Bot, products):
    """Sends product list that need to sell"""
    products_for_sale = []
    for product in products:
        shelf_life = abs(((datetime.now()) - datetime.strptime(product[2], "%d.%m.%y")).days)
        if shelf_life <= 4:
            products_for_sale.append(product)
    sorted_products = sorted(products_for_sale, key=lambda x: datetime.strptime(x[2], "%d.%m.%y"))
    sorted_products = "\n".join(
        f"{product_index + 1}.{str(sorted_products[product_index])}" for product_index in range(len(sorted_products))
        )
    message = f"Эти товары желательно продать:\n{sorted_products}"
    await bot.send_message(-945893857, message)

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup


def menu_kb():
    """Returns menu kb"""
    menu_list = InlineKeyboardMarkup(row_width=2)
    menu_list.add(InlineKeyboardButton(text="Добавить продкут", callback_data="add_product"),
                  InlineKeyboardButton(text="Удалить продкут", callback_data="delete_product"),
                  InlineKeyboardButton(text="Список продкутов", callback_data="products_list"))
    return menu_list


def categories_kb(categories):
    """Returns category kb"""
    categories_list = ReplyKeyboardMarkup(resize_keyboard=True)
    for category_name in categories:
        categories_list.add(f"{category_name[0]}")
    return categories_list

import os
from datetime import datetime
from db import DataBase
from kb import menu_kb, categories_kb
from scheduled_tasks import send_message_cron
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.dispatcher import FSMContext
from apscheduler.schedulers.asyncio import AsyncIOScheduler


load_dotenv()

storage = MemoryStorage()
bot = Bot(os.getenv("TOKEN"))
db = Dispatcher(bot, storage=storage)
database = DataBase("store")


class ProductAddingStatesGroup(StatesGroup):
    """State for adding product to the db"""
    product_number = State()
    name = State()
    category = State()
    shelf_life = State()


class ProductDeletingStatesGroup(StatesGroup):
    """State for deleting product from the db"""
    product_number = State()
    shelf_life = State()


async def on_startup(_):
    if not database.check_table():
        database.create_tables()
    print("Bot has been connected!")


def setup_scheduler(bot):
    """Function that sends products at a certain time to the chat"""
    scheduler = AsyncIOScheduler(timezone="Europe/Kiev")
    scheduler.add_job(send_message_cron, trigger="cron", hour=6, minute=0,
                      start_date=datetime.now(), kwargs={"bot": bot, "products": database.get_products()})
    scheduler.start()
    return scheduler


if database.check_table():
    scheduler = setup_scheduler(bot)


@db.message_handler(commands=["menu"])
async def cmd_menu(message: types.Message):
    """Control panel"""
    await message.answer("Это панель управления", reply_markup=menu_kb())


@db.callback_query_handler(lambda callback_query: callback_query.data == "delete_product")
async def delete_product(callback: types.CallbackQuery):
    """Adds product number to the ProductDeletingStatesGroup"""
    await callback.message.answer("Введите код продукта")
    await ProductDeletingStatesGroup.product_number.set()


@db.message_handler(lambda message: not message.text.isdigit() or len(message.text) != 5, state=ProductDeletingStatesGroup.product_number)
async def check_deleted_product_number(message: types.Message):
    """Product number verification"""
    await message.answer("Номер продукта введен не корректно!")


@db.message_handler(state=ProductDeletingStatesGroup.product_number)
async def delete_product_number(message: types.Message, state: FSMContext):
    """Adds product shelf life to the ProductDeletingStatesGroup"""
    async with state.proxy() as data:
        data["product_number"] = message.text

    await message.answer("Введите срок годности продукта в таком формате: дд.мм.гг")
    await ProductDeletingStatesGroup.next()


@db.message_handler(state=ProductDeletingStatesGroup.shelf_life)
async def delete_product_shelf_life(message: types.Message, state: FSMContext):
    """Delete product from data base"""
    async with state.proxy() as data:
        data["shelf_life"] = message.text

        database.delete_product(
            product_number=data["product_number"],
            shelf_life=data["shelf_life"]
        )

    await message.answer("Продукт успешно удален")
    await state.finish()



@db.callback_query_handler(lambda callback_query: callback_query.data == "add_product")
async def add_product(callback: types.CallbackQuery):
    """Adds product number to the ProductAddingStatesGroup"""
    await callback.message.answer("Введите код продукта")
    await ProductAddingStatesGroup.product_number.set()


@db.message_handler(lambda message: not message.text.isdigit(), state=ProductAddingStatesGroup.product_number)
async def check_added_product_number(message: types.Message):
    """Product number verification"""
    await message.answer("Код продукта введен не корректно!")


@db.message_handler(state=ProductAddingStatesGroup.product_number)
async def load_product_number(message: types.Message, state: FSMContext):
    """Adds product name to the ProductAddingStatesGroup"""
    async with state.proxy() as data:
        data["product_number"] = message.text

    await message.answer("Введите название продукта")
    await ProductAddingStatesGroup.next()


@db.message_handler(lambda message: not message.text.replace(" ", "").isalpha(), state=ProductAddingStatesGroup.name)
async def check_name(message: types.Message):
    """Product name verification"""
    await message.answer("Название продукта введено не верно!")


@db.message_handler(state=ProductAddingStatesGroup.name)
async def load_name(message: types.Message, state: FSMContext):
    """Adds product category to the ProductAddingStatesGroup"""
    async with state.proxy() as data:
        data["name"] = message.text

    await message.answer("Выбери категорию продукта", reply_markup=categories_kb(database.get_categories()))
    await ProductAddingStatesGroup.next()


@db.message_handler(state=ProductAddingStatesGroup.category)
async def load_category(message: types.Message, state: FSMContext):
    """Adds product shelf life to the ProductAddingStatesGroup"""
    async with state.proxy() as data:
        data["category"] = message.text

    await message.answer("Введите срок годности продукта в таком формате: дд.мм.гг")
    await ProductAddingStatesGroup.next()


def is_valid_shelf_life(date):
    """Checks product's shelf life is valid"""
    try:
        shelf_life = (datetime.now() - datetime.strptime(date.text, "%d.%m.%y")).days
        if shelf_life > 0:
            return True
    except(TypeError, ValueError):
        return True
    return False


@db.message_handler(is_valid_shelf_life, state=ProductAddingStatesGroup.shelf_life)
async def check_shelf_life(message: types.Message):
    await message.answer("Дата введена не корректно!")


@db.message_handler(state=ProductAddingStatesGroup.shelf_life)
async def load_shelf_life(message: types.Message, state: FSMContext):
    """Adds product to the data base"""
    async with state.proxy() as data:
        data["shelf_life"] = message.text

        database.add_product(
            product_number=data["product_number"],
            name=data["name"],
            category=data["category"],
            shelf_life=data["shelf_life"]
        )
    await message.answer("Продукт успешно добавлен!")
    await state.finish()


@db.callback_query_handler(lambda callback_query: callback_query.data == "products_list")
async def get_products(callback: types.CallbackQuery):
    """Sends a sorted product list"""
    sorted_products = sorted(database.get_products(), key=lambda x: datetime.strptime(x[2], "%d.%m.%y"))
    sorted_products = "Список продуктов:\n" + "\n".join(
        f"{product_index + 1}.{str(sorted_products[product_index])}" for product_index in range(len(sorted_products))
        )
    await callback.message.answer(sorted_products)


if __name__ == "__main__":
    executor.start_polling(db, on_startup=on_startup, skip_updates=True)

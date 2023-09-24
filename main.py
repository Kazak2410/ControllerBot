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
    product_number = State()
    name = State()
    category = State()
    shelf_life = State()


class ProductDeletingStatesGroup(StatesGroup):
    product_number = State()
    shelf_life = State()


async def on_startup(_):
    if not database.check_table():
        database.create_tables()
    print("Bot has been connected!")


def setup_scheduler(bot):
    scheduler = AsyncIOScheduler(timezone="Europe/Kiev")
    scheduler.add_job(send_message_cron, trigger="cron", hour=19, minute=36,
                      start_date=datetime.now(), kwargs={"bot": bot, "products": database.get_products()})
    scheduler.start()
    return scheduler


scheduler = setup_scheduler(bot)


@db.message_handler(commands=["menu"])
async def cmd_menu(message: types.Message):
    await message.answer("Это панель управления", reply_markup=menu_kb())


@db.callback_query_handler(lambda callback_query: callback_query.data == "delete_product")
async def delete_product(callback: types.CallbackQuery):
    await callback.message.answer("Введите код продукта")
    await ProductDeletingStatesGroup.product_number.set()


@db.message_handler(state=ProductDeletingStatesGroup.product_number)
async def delete_product_number(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["product_number"] = message.text

    await message.answer("Введите срок годности продукта в таком формате: дд.мм.гг")
    await ProductDeletingStatesGroup.next()


@db.message_handler(state=ProductDeletingStatesGroup.shelf_life)
async def delete_product_shelf_life(message: types.Message, state: FSMContext):
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
    await callback.message.answer("Введите код продукта")
    await ProductAddingStatesGroup.product_number.set()


@db.message_handler(lambda message: not message.text.isdigit(), state=ProductAddingStatesGroup.product_number)
async def check_id(message: types.Message):
    await message.answer("Код продукта введен не корректно!")


@db.message_handler(state=ProductAddingStatesGroup.product_number)
async def load_product_number(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["product_number"] = message.text

    await message.answer("Введите название продукта")
    await ProductAddingStatesGroup.next()


@db.message_handler(lambda message: not message.text.replace(" ", "").isalpha(), state=ProductAddingStatesGroup.name)
async def check_name(message: types.Message):
    await message.answer("Название продукта введено не верно!")


@db.message_handler(state=ProductAddingStatesGroup.name)
async def load_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["name"] = message.text

    await message.answer("Выбери категорию продукта", reply_markup=categories_kb(database.get_categories()))
    await ProductAddingStatesGroup.next()


@db.message_handler(state=ProductAddingStatesGroup.category)
async def load_category(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["category"] = message.text

    await message.answer("Введите срок годности продукта в таком формате: дд.мм.гг")
    await ProductAddingStatesGroup.next()


@db.message_handler(state=ProductAddingStatesGroup.shelf_life)
async def load_shelf_life(message: types.Message, state: FSMContext):
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
    await callback.message.answer(database.get_products())


if __name__ == "__main__":
    executor.start_polling(db, on_startup=on_startup, skip_updates=True)

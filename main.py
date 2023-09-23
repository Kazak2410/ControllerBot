import os
from db import DataBase
from kb import menu_kb, categories_kb
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.dispatcher import FSMContext


load_dotenv()

storage = MemoryStorage()
bot = Bot(os.getenv("TOKEN"))
db = Dispatcher(bot, storage=storage)
database = DataBase("store")


class ProductStatesGroup(StatesGroup):
    product_id = State()
    name = State()
    category = State()
    shelf_life = State()


async def on_startup(_):
    if not database.check_table():
        database.create_tables()
    print("Bot has been connected!")


@db.message_handler(commands=["start"])
async def cmd_start(message: types.Message):
    await message.answer("Список категорий", reply_markup=categories_kb(database.get_categories()))


@db.message_handler(commands=["menu"])
async def cmd_menu(message: types.Message):
    await message.answer("Это панель управления", reply_markup=menu_kb())


@db.callback_query_handler(lambda callback_query: callback_query.data == "add_product")
async def add_product(callback: types.CallbackQuery):
    await callback.message.answer(f"Введите код продукта")
    await ProductStatesGroup.product_id.set()


@db.message_handler(lambda message: not message.text.isdigit(), state=ProductStatesGroup.product_id)
async def check_id(message: types.Message):
    await message.answer("Код продукта введен не корректно!")


@db.message_handler(state=ProductStatesGroup.product_id)
async def load_product_id(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["product_id"] = message.text

    await message.answer("Введите название продукта")
    await ProductStatesGroup.next()


@db.message_handler(lambda message: not message.text.replace(" ", "").isalpha(), state=ProductStatesGroup.name)
async def check_name(message: types.Message):
    await message.answer("Название продукта введено не верно!")


@db.message_handler(state=ProductStatesGroup.name)
async def load_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["name"] = message.text

    await message.answer("Выбери категорию продукта", reply_markup=categories_kb(database.get_categories()))
    await ProductStatesGroup.next()


@db.message_handler(state=ProductStatesGroup.category)
async def load_category(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["category"] = message.text

    await message.answer("Введите срок годности продукта в таком формате: дд.мм.гг")
    await ProductStatesGroup.next()


@db.message_handler(state=ProductStatesGroup.shelf_life)
async def load_shelf_life(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["shelf_life"] = message.text

        database.add_product(
            product_number=data["product_id"],
            name=data["name"],
            category=data["category"],
            shelf_life=data["shelf_life"]
        )
    await message.answer("Продукт успешно добавлен!")
    await state.finish()


if __name__ == "__main__":
    executor.start_polling(db, on_startup=on_startup, skip_updates=True)

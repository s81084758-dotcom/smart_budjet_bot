import asyncio
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from database import db
from state import Form
import keyboards as kb
import utils

TOKEN = "8762038887:AAHwGfxr8vx62uiCKcBsYdK2w_JTAiRCdVk"

bot = Bot(token=TOKEN)
dp = Dispatcher()


# START
@dp.message(Command("start"))
async def start_cmd(message: Message):
    db.add_user(message.from_user.id, message.from_user.full_name)

    await message.answer(
        f"Salom {message.from_user.full_name}!\nSmartBudget botga xush kelibsiz.",
        reply_markup=kb.main_menu()
    )



def ensure_user(message):
    user = db.get_user(message.from_user.id)
    if not user:
        db.add_user(message.from_user.id, message.from_user.full_name)
        user = db.get_user(message.from_user.id)
    return user

# BYUDJET
@dp.message(F.text == "💰 Byudjet")
async def show_budget(message: Message):
    user = db.get_user(message.from_user.id)
    total = db.get_monthly_total(message.from_user.id)

    currency = user[3]
    limit = user[4]

    total = utils.convert_currency(total, "UZS", currency)
    limit_conv = utils.convert_currency(limit, "UZS", currency)

    percent = (total / limit_conv * 100) if limit > 0 else 0

    text = (
        f"💰 Byudjet:\n\n"
        f"Limit: {limit_conv:,.0f} {currency}\n"
        f"Sarf: {total:,.0f} {currency}\n"
        f"Foiz: {percent:.1f}%"
    )

    await message.answer(text, reply_markup=kb.budget_inline())


# LIMIT SO‘RASH
@dp.callback_query(F.data == "set_budget_limit")
async def ask_budget(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Limitni kiriting:")
    await state.set_state(Form.waiting_for_budget)
    await callback.answer()


# LIMIT SAQLASH
@dp.message(Form.waiting_for_budget)
async def save_budget(message: Message, state: FSMContext):
    if not message.text.isdigit():
        return await message.answer("Faqat raqam kiriting!")

    limit = int(message.text)
    db.update_budget(message.from_user.id, limit)

    await message.answer("✅ Limit saqlandi", reply_markup=kb.main_menu())
    await state.clear()


# SOZLAMALAR
@dp.message(F.text == "⚙️ Sozlamalar")
async def settings(message: Message):
    user = db.get_user(message.from_user.id)

    await message.answer(
        f"Valyuta: {user[3]}",
        reply_markup=kb.settings_inline()
    )


# VALYUTA TANLASH
@dp.callback_query(F.data == "set_cur")
async def choose_currency(callback: CallbackQuery):
    await callback.message.edit_text(
        "Valyutani tanlang:",
        reply_markup=kb.currency_inline()
    )


@dp.callback_query(F.data.startswith("cur_"))
async def save_currency(callback: CallbackQuery):
    cur = callback.data.split("_")[1]
    db.update_currency(callback.from_user.id, cur)

    await callback.message.answer(f"✅ {cur} tanlandi")
    await callback.answer()


# XARAJAT QO‘SHISH
@dp.message(F.text == "➕ Xarajat qo'shish")
async def add_expense(message: Message):
    await message.answer("Kategoriya tanlang:", reply_markup=kb.category_keyboard())


@dp.callback_query(F.data.startswith("cat_"))
async def select_category(callback: CallbackQuery, state: FSMContext):
    cat = callback.data.split("_")[1]

    await state.update_data(cat=cat)
    await state.set_state(Form.waiting_for_amount)

    await callback.message.answer("Summani kiriting:")
    await callback.answer()


@dp.message(Form.waiting_for_amount)
async def save_expense(message: Message, state: FSMContext):
    if not message.text.isdigit():
        return await message.answer("Faqat raqam!")

    data = await state.get_data()
    amount = int(message.text)

    user = db.get_user(message.from_user.id)
    currency = user[3]

    if currency == "USD":
        amount = utils.convert_currency(amount, "USD", "UZS")

    db.add_expense(message.from_user.id, data['cat'], amount)

    await message.answer("✅ Saqlandi", reply_markup=kb.main_menu())
    await state.clear()


# HISOBOT
@dp.message(F.text == "📊 Hisobot")
async def report(message: Message):
    user = db.get_user(message.from_user.id)
    currency = user[3]

    data = db.get_monthly_report(message.from_user.id)

    if not data:
        return await message.answer("Ma'lumot yo‘q")

    text = "📊 Hisobot:\n\n"
    total = 0

    for name, emoji, amount in data:
        amount = utils.convert_currency(amount, "UZS", currency)
        total += amount
        text += f"{emoji} {name}: {amount:,.0f} {currency}\n"

    text += f"\nJami: {total:,.0f} {currency}"

    await message.answer(text)


# RUN
async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
import sys
import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from state import Form

from database import db
import keyboards as kb
import utils

TOKEN = "8762038887:AAHwGfxr8vx62uiCKcBsYdK2w_JTAiRCdVk"
bot = Bot(token=TOKEN)
dp = Dispatcher()


@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    db.add_user(message.from_user.id, message.from_user.full_name)
    await message.answer(
        f"Salom {message.from_user.full_name}! SmartBudget botiga xush kelibsiz.\n"
        f"Pastdagi tugmalardan foydalaning.", 
        reply_markup=kb.main_menu()
    )

@dp.message(F.text == "💰 Byudjet")
async def show_budget(message: types.Message):
    user = db.get_user(message.from_user.id)

    total_spent = db.get_monthly_total(message.from_user.id)

    currency = user[3]
    limit = user[4]

    # 🔥 convert
    total_spent = utils.convert_currency(total_spent, "UZS", currency)
    limit_conv = utils.convert_currency(limit, "UZS", currency)

    status = "Belgilanmagan" if limit == 0 else f"{limit_conv:,.2f} {currency}"
    percent = (total_spent / limit_conv * 100) if limit > 0 else 0

    text = (f"💰 **Byudjet holati:**\n\n"
            f"💵 Limit: {status}\n"
            f"💸 Sarflandi: {total_spent:,.2f} {currency}\n"
            f"📊 Foizda: {percent:.1f}%")

    await message.answer(text, reply_markup=kb.budget_inline(), parse_mode="Markdown")

@dp.callback_query(F.data == "set_budget_limit")
async def ask_budget(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("Yangi oylik limitni raqamda kiriting:")
    await state.set_state(Form.waiting_for_budget)
    await callback.answer()

@dp.message(Form.waiting_for_budget)
async def process_budget(message: types.Message, state: FSMContext):
    if message.text.isdigit():
        user = db.get_user(message.from_user.id)
        limit = int(message.text)
        db.update_budget(message.from_user.id, limit)
        await message.answer(f"✅ Limit {limit:,} {user[3]} qilib belgilandi.", reply_markup=kb.main_menu())
        await state.clear()
    else:
        await message.answer("Iltimos, faqat raqam kiriting!")

@dp.message(F.text == "⚙️ Sozlamalar")
async def show_settings(message: types.Message):
    user = db.get_user(message.from_user.id)
    text = (f"⚙️ **Sozlamalar**\n\n"
            f"👤 Ism: {user[2]}\n"
            f"💱 Hozirgi valyuta: {user[3]}")
    await message.answer(text, reply_markup=kb.settings_inline(), parse_mode="Markdown")

@dp.callback_query(F.data == "set_cur")
async def change_currency_call(callback: types.CallbackQuery):
    await callback.message.edit_text("Yangi valyutani tanlang:", reply_markup=kb.currency_inline())

@dp.callback_query(F.data.startswith("cur_"))
async def save_currency(callback: types.CallbackQuery):
    new_cur = callback.data.split("_")[1]
    db.update_currency(callback.from_user.id, new_cur)
    await callback.message.answer(f"✅ Valyuta muvaffaqiyatli {new_cur} ga o'zgartirildi!")
    await callback.answer()

@dp.message(F.text == "➕ Xarajat qo'shish")
async def add_exp(message: types.Message):
    await message.answer("Kategoriyani tanlang:", reply_markup=kb.category_keyboard())

@dp.callback_query(F.data.startswith("cat_"))
async def select_cat(callback: types.CallbackQuery, state: FSMContext):
    cat = callback.data.split("_")[1]
    await state.update_data(chosen_cat=cat)
    await callback.message.edit_text(f"Kategoriya: {cat}\nSummani kiriting:")
    await state.set_state(Form.waiting_for_amount)

@dp.message(Form.waiting_for_amount)
async def save_exp(message: types.Message, state: FSMContext):
    if message.text.isdigit():
        data = await state.get_data()
        amount = int(message.text)

        user = db.get_user(message.from_user.id)
        currency = user[3]

        # 🔥 UZS ga konvertatsiya qilamiz
        if currency == "USD":
            amount = utils.convert_currency(amount, "USD", "UZS")

        db.add_expense(message.from_user.id, data['chosen_cat'], amount)

        total = db.get_monthly_total(message.from_user.id)
        limit = user[4]

        # chiqarishda qayta konvertatsiya qilamiz
        display_amount = utils.convert_currency(amount, "UZS", currency)
        display_total = utils.convert_currency(total, "UZS", currency)

        await message.answer(f"✅ Saqlandi: {display_amount:,.2f} {currency}", reply_markup=kb.main_menu())

        if limit > 0:
            display_limit = utils.convert_currency(limit, "UZS", currency)
            if total > limit:
                await message.answer(
                    f"⚠️ **DIQQAT!**\n"
                    f"Limit: {display_limit:,.2f} {currency}\n"
                    f"Sarf: {display_total:,.2f} {currency}",
                    parse_mode="Markdown"
                )

        await state.clear()
    else:
        await message.answer("Faqat raqam kiriting!")

@dp.message(F.text == "📊 Hisobot")
async def send_report(message: types.Message):
    user = db.get_user(message.from_user.id)
    currency = user[3]

    data = db.get_monthly_report(message.from_user.id)

    if not data:
        return await message.answer("Ma'lumot topilmadi.")

    report_text = f"📊 **Oylik Hisobot**\n\n"
    total = 0

    for row in data:
        amount = utils.convert_currency(row[2], "UZS", currency)
        total += amount
        report_text += f"{row[1]} {row[0]}: {amount:,.2f} {currency}\n"

    report_text += f"\n💰 **Jami: {total:,.2f} {currency}**"

    await message.answer(report_text, parse_mode="Markdown")

async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot to'xtadi")
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

def main_menu():
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="📊 Hisobot"), KeyboardButton(text="➕ Xarajat qo'shish")],
        [KeyboardButton(text="💰 Byudjet"), KeyboardButton(text="⚙️ Sozlamalar")]
    ], resize_keyboard=True)

def settings_inline():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💱 Valyutani o'zgartirish", callback_data="set_cur")]
    ])

def currency_inline():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="So'm (UZS)", callback_data="cur_UZS"),
         InlineKeyboardButton(text="Dollar (USD)", callback_data="cur_USD")]
    ])

def budget_inline():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🆕 Limit o'rnatish", callback_data="set_budget_limit")]
    ])

def category_keyboard():
    categories = ['Ovqat', 'Transport', 'Uy', 'Sog\'liq', 'Ko\'ngil ochar', 'Ta\'lim', 'Kiyim', 'Boshqa']
    buttons = []
    for i in range(0, len(categories), 2):
        row = [
            InlineKeyboardButton(text=categories[i], callback_data=f"cat_{categories[i]}"),
            InlineKeyboardButton(text=categories[i+1], callback_data=f"cat_{categories[i+1]}")
        ]
        buttons.append(row)
    return InlineKeyboardMarkup(inline_keyboard=buttons)
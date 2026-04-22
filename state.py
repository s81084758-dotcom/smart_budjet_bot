from aiogram.fsm.state import State, StatesGroup




class Form(StatesGroup):
    waiting_for_amount = State()
    waiting_for_budget = State()

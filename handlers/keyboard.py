from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main = ReplyKeyboardMarkup(resize_keyboard=True)
b1 = KeyboardButton("/last")
b2 = KeyboardButton("/week")
b3 = KeyboardButton("/month")
# main.add(b2, b3).add(b5, b4)
main.add(b1, b2, b3)

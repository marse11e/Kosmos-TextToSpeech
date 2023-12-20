from telebot import types


def get_main_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    
    button1 = types.KeyboardButton("Озвучить")
    button2 = types.KeyboardButton("Профиль")
    button3 = types.KeyboardButton("Купить попытку")
    
    keyboard.row(button1, button2)
    keyboard.row(button3)
    
    return keyboard


def get_cancel_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    
    button1 = types.KeyboardButton("Отмена")
    
    keyboard.row(button1)
    
    return keyboard

def get_buy_attempts():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    
    button1 = types.KeyboardButton("Купить попытку")
    button2 = types.KeyboardButton("Отмена")
    
    keyboard.row(button1)
    keyboard.row(button2)
    
    return keyboard

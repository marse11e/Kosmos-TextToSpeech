import logging
import secrets

import telebot
from telebot import types

from django.conf import settings
from main.models import Text_to_speech
from telegrambot.models import TelegramUser, TryTransform

from .keyboards import get_cancel_keyboard, get_main_keyboard, get_buy_attempts

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

bot = telebot.TeleBot(settings.TOKENBOT)


@bot.message_handler(commands=['start'])
def start(message):
    user = message.from_user

    telegram_user, created = TelegramUser.objects.get_or_create(user_id=user.id)
    
    if created:
        telegram_user.user_id = user.id
        telegram_user.username = user.username
        telegram_user.first_name = user.first_name
        telegram_user.last_name = user.last_name
        telegram_user.language_code = user.language_code
        telegram_user.is_bot = user.is_bot
        telegram_user.save()
        
        logging.info(f'New user {user.username} created')
        
    bot.send_message(message.chat.id, f'Привет {telegram_user.get_name()}',
                     reply_markup=get_main_keyboard())


def text_to_speech(message):
    if message.text.lower() == 'отмена':
        bot.send_message(message.chat.id, 'Вы отменили действие!', reply_markup=get_main_keyboard())
    else:
        text_for_speech = Text_to_speech(
            text=message.text,
            file_name=message.from_user.id,
        )
        text_for_speech.save()
        
        with open(text_for_speech.path_file.path, 'rb') as f:   
            bot.send_voice(message.chat.id, f.read(), caption=text_for_speech.text, 
                reply_markup=get_main_keyboard())
    
        try_transform = TryTransform.objects.get(
            tuser=TelegramUser.objects.get(user_id=message.from_user.id)
        )        
        try_transform.count -= 1
        try_transform.save()


@bot.message_handler(func=lambda message: message.text.lower() == 'озвучить')
def voice_over(message):
    try_transform = TryTransform.objects.get(
        tuser=TelegramUser.objects.get(user_id=message.from_user.id)
    )  
    if try_transform.count > 0:
        text = (
            "Пожалуйста напимне текст для преобразования, не более 700 букв\n"
            "Напиример: Привет Антоха\n\n"
            f"У вас осталось попыток: {try_transform.count}"
        )
        
        bot.send_message(message.chat.id, text, reply_markup=get_cancel_keyboard())
        bot.register_next_step_handler(message, text_to_speech)
    else:
        bot.send_message(message.chat.id, "У вас закончились попытки!", 
            reply_markup=get_buy_attempts())


def get_photo_profile(message):
    user_id = message.from_user.id
    photos = bot.get_user_profile_photos(user_id, limit=1)

    if photos.photos:
        file_id = photos.photos[0][-1].file_id
        return file_id


@bot.message_handler(func=lambda message: message.text.lower() == 'профиль')
def profile(message):
    try:
        tuser = TelegramUser.objects.get(user_id=message.from_user.id)
        try_transform = TryTransform.objects.get(tuser=tuser)

        info = (
            f"ID пользователя: {tuser.user_id}\n"
            f"Имя пользователя: {tuser.username}\n"
            f"Фамилия: {tuser.last_name}\n"
            f"Имя: {tuser.first_name}\n"
            f"Пользователь бот: {'Да' if tuser.is_bot else 'Нет'}\n"
            f"Код языка: {tuser.language_code}\n"
            f"Количество попыток преобразования: {try_transform.count}"
        )

        bot.send_photo(
            message.chat.id,
            photo=get_photo_profile(message),
            caption=info,
            reply_markup=get_main_keyboard()
        )
        
    except TelegramUser.DoesNotExist:
        bot.send_message(message.chat.id, "Пользователь не найден.", 
            reply_markup=get_main_keyboard())
        
    except TryTransform.DoesNotExist:
        bot.send_message(message.chat.id, "Информация о преобразованиях не найдена.", 
            reply_markup=get_main_keyboard())
        
    except Exception as e:
        bot.send_message(message.chat.id, f"Произошла ошибка: {str(e)}", 
            reply_markup=get_main_keyboard())
    

def run_bot():
    try:
        logger = logging.getLogger(__name__)
        logger.info("Бот начал работу")
        bot.polling()
        
    except Exception as e:
        logger.error(f"Произошла ошибка: {e}")
        
    except KeyboardInterrupt:
        logger.info("Бот остановлен принудительно!")
        
    finally:
        logger.info("Бот завершил работу")

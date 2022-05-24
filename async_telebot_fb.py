import logging
from aiogram import Bot, Dispatcher, executor, types
import os
from aiogram.utils.exceptions import BotBlocked, NetworkError
from aiogram.utils.callback_data import CallbackData
from aiogram.dispatcher.filters import Text
from aiogram.utils.exceptions import MessageNotModified
from contextlib import suppress
from numpy import std
import my_moving_average
import robot_fatbold
import asyncio


BOT_TOKEN = os.environ["INVEST_BOT_TOKEN"]                             
password = os.environ["INVEST_BOT_PASSWORD"]               

#Переключатели для понимания в каком состоянии находится торговый робот
#if robot_must_work == False, то при следующем выходе из генератора, цикл прервется и торговый робот будет отключен. 
trade_robot_states = {
    "status_trade_robot": False,
    "robot_must_work": True
}

# Объект бота
bot = Bot(token = BOT_TOKEN)
# Диспетчер для бота
dp = Dispatcher(bot)
# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)

help = """
/help - показывает подсказку \n
/set - устанавливает настройки \n
Cообщение "Запустить торгового робота" запускает робота с настройками,
которые ты задал или настройками по умолчанию. \n
Cообщение "Остановить торгового робота" останавливает робота примерно за 60 сек. \n
Cообщение "Настройки" показывает способ задать настройки \n

Робот работает по стратегии: \n
 short_ma > long_ma открывает позицию \n
 short_ma < long_ma продает акции \n


"""


long_ma = 15
short_ma = 3
std_period = 5

user_data = {
    'long_ma': long_ma,
    'short_ma': short_ma,
    'std_period': std_period
}

def get_keyboard_fab(parametr:str) -> types.InlineKeyboardMarkup:
    buttons = [
        types.InlineKeyboardButton(text="-1", callback_data=callback_numbers.new(parametr = parametr, action="decr")),
        types.InlineKeyboardButton(text="+1", callback_data=callback_numbers.new(parametr = parametr, action="incr")),
        types.InlineKeyboardButton(text="Подтвердить", callback_data=callback_numbers.new(parametr = parametr, action="finish"))
    ]
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(*buttons)
    return keyboard


async def update_num_text_fab(message: types.Message, parametr: str, new_value: int):
    with suppress(MessageNotModified):
        await message.edit_text(f"Укажите значение {parametr}: {new_value}", reply_markup=get_keyboard_fab(parametr))


callback_numbers = CallbackData("sets","parametr", "action")

@dp.callback_query_handler(callback_numbers.filter(parametr = "long_ma", action=["incr", "decr"]))
async def callbacks_num_change_long_ma(call: types.CallbackQuery, callback_data: dict):
    
    user_value = user_data["long_ma"]
    action = callback_data["action"]
    parametr = callback_data["parametr"]

    if action == "incr":
        user_data["long_ma"] = user_value + 1
        await update_num_text_fab(call.message, parametr, user_value + 1)
    elif action == "decr":
        user_data["long_ma"] = user_value - 1
        await update_num_text_fab(call.message, parametr, user_value - 1)
    await call.answer()

@dp.callback_query_handler(callback_numbers.filter(parametr = "short_ma", action=["incr", "decr"]))
async def callbacks_num_change_long_ma(call: types.CallbackQuery, callback_data: dict):
    
    user_value = user_data["short_ma"]
    action = callback_data["action"]
    parametr = callback_data["parametr"]

    if action == "incr":
        user_data["short_ma"] = user_value + 1
        await update_num_text_fab(call.message, parametr, user_value + 1)
    elif action == "decr":
        user_data["short_ma"] = user_value - 1
        await update_num_text_fab(call.message, parametr, user_value - 1)
    await call.answer()

@dp.callback_query_handler(callback_numbers.filter(parametr = "std_period", action=["incr", "decr"]))
async def callbacks_num_change_long_ma(call: types.CallbackQuery, callback_data: dict):
    
    user_value = user_data["std_period"]
    action = callback_data["action"]
    parametr = callback_data["parametr"]

    if action == "incr":
        user_data["std_period"] = user_value + 1
        await update_num_text_fab(call.message, parametr, user_value + 1)
    elif action == "decr":
        user_data["std__period"] = user_value - 1
        await update_num_text_fab(call.message, parametr, user_value - 1)
    await call.answer()

@dp.callback_query_handler(callback_numbers.filter(parametr = ["long_ma","short_ma", "std_period"], action=["finish"]))
async def callbacks_num_finish_fab(call: types.CallbackQuery, callback_data: dict):
    
    parametr = callback_data["parametr"]
    user_value = user_data[parametr]
    await call.message.edit_text(f"Установлено значение {parametr}: {user_value}")
    await call.message.answer("Настройки")


@dp.message_handler(commands="start")
async def cmd_start(message: types.Message):
    
    await message.answer("Введите пароль")

@dp.message_handler(Text(equals="главное меню"))
async def main_menu(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True,row_width=2)
    buttons = [
    "Запустить торгового робота", 
    "Тест в песочнице",
    "Настройки",
    "Инструкция",
    "Баланс"    
    ]
    keyboard.add(*buttons)
    await message.answer("Что делать, хозяин?", reply_markup=keyboard)

    
@dp.message_handler(commands=password)
async def cmd_password(message: types.Message):
    """Запускает бота"""
    greeting = """Привет! Я робот. Меня зовут Толстый жирный. \n Я умею торговать на бирже. И делать твое депо толстым и жирным. \n
    Ты можешь ввести команду /help и прочитать инструкцию по работе со мной. \n Она выглядит так:"""
    await message.answer(greeting)    
    await message.answer(help)

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True,row_width=2)
    buttons = [
    "Запустить торгового робота", 
    "Тест в песочнице",
    "Настройки",
    "Инструкция",
    "Баланс"    
    ]
    keyboard.add(*buttons)
    await message.answer("Что делать, хозяин?", reply_markup=keyboard)


    
@dp.message_handler(Text(equals="Запустить торгового робота"))
async def start_trade(message: types.Message):
    
    
    if trade_robot_states["status_trade_robot"] == False: 

        status = "Working"

        gen = robot_fatbold.main(long_ma = user_data["long_ma"],short_ma = user_data["short_ma"], std_period = user_data["std_period"])

        flag = True #Чтобы один раз сообщить, что робот запущен.

        while status ==  "Working" and  trade_robot_states["robot_must_work"]:
            response = await gen.__anext__()
           
            trade_robot_states["status_trade_robot"] = True
           
            status = response['status'] 
            
            await asyncio.sleep(0.1)
            
            if flag and status == "Working":
                keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True,row_width=2)
                buttons = [
                "Остановить торгового робота",
                "Тест в песочнице",
                "Настройки",
                "Инструкция",
                "Баланс"    
                ]
                keyboard.add(*buttons)
                await message.answer("Торговый робот запущен!",reply_markup=keyboard)
                flag = False
                trade_robot_states["status_trade_robot"] = True
                trade_robot_states["robot_must_work"] = True

            #status = response['status']
            #Робот работает ничего не делаем
        
        trade_robot_states["status_trade_robot"] = False #Изменим статус
        trade_robot_states["robot_must_work"] = True #Поднимим флаг, чтобы робот мог запуститься
        balance = response['balance']
        profit = response['profit']
        shares = response['shares']
        send_message = f"""
        Робот остановлен.
        Текущий cтатус: {status} \n
        Сумма на счете: {balance:.2f} \n
        Стоимость акций: {shares:.2f} \n
        Прибыль с момента запуска: {profit:.2f}
        """
        

        await message.answer(send_message)
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True,row_width=2)
        buttons = [
        "Запустить торгового робота", 
        "Тест в песочнице",
        "Настройки",
        "Инструкция",
        "Баланс"    
        ]
        keyboard.add(*buttons)
        await message.answer("Что делать, хозяин?", reply_markup=keyboard)
        
    elif trade_robot_states["status_trade_robot"] == True:
        await message.answer("Робот уже запущен") 
    else:
        await message.answer("Робот в непонятном состоянии") 



@dp.message_handler(lambda message: message.text == "Остановить торгового робота")
async def stop_trade(message: types.Message):

    if trade_robot_states['status_trade_robot'] == True: 
        trade_robot_states['robot_must_work'] = False #Глобальная переменная для остановки робота
    else:        
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True,row_width=2)
        buttons = [
        "Запустить торгового робота", 
        "Тест в песочнице",
        "Настройки",
        "Инструкция",
        "Баланс"    
        ]
        keyboard.add(*buttons)
        
        await message.answer("Робот и так не работал", reply_markup=keyboard)

@dp.message_handler(lambda message: message.text == "Тест в песочнице")
async def sandbox_test(message: types.Message):
    send_message = "Запущен тест на песочнице:"
    await message.answer(send_message)

    results = my_moving_average.main(start_balance_units = 100000, long_ma_min = 13, long_ma_max = 15, short_ma_min = 3, short_ma_max = 4, std_period_min = 5,  std_period_max = 6)

    send_message = "Тест на песочнице закончен:"
    await message.answer(send_message)

    best_settings = results[0]['settings']
    best_result_message = f"""
    Лучшие настройки:
    Прибыль: {float(results[0]['profit']):.2f} 
    Инструмент: {best_settings['stock']}
    long_ma: {best_settings['long_ma']}
    short_ma: {best_settings['short_ma']}
    std_period: {best_settings['std_period']}
    tf: {best_settings['tf']}
    period: {best_settings['period']}
    """

    await message.answer(best_result_message)

    send_message = "Остальные результаты:"
    await message.answer(send_message)

    for i in range(1,len(results)):
        settings = results[i]['settings']
        result_message = f"""
        Прибыль: {float(results[i]['profit']):.2f} 
        Инструмент: {settings['stock']} 
        long_ma: {settings['long_ma']}
        short_ma: {settings['short_ma']}
        std_period: {settings['std_period']}
        tf: {settings['tf']}
        period: {settings['period']}
        """
        await message.answer(result_message)

@dp.message_handler(lambda message: message.text == "Настройки")
async def sittings_setup(message: types.Message):

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True,row_width=1)
    buttons = [
    "long_ma", 
    "short_ma",
    "std_period",
    "главное меню"
    ]
    keyboard.add(*buttons)
    await message.answer("Выберите параметр:", reply_markup=keyboard)
    
    
    
@dp.message_handler(lambda message: message.text == "long_ma")
async def sittings_setup(message: types.Message):

    user_value = user_data["long_ma"]
    
    await message.answer(f"Укажите значение long_ma: {user_value}", reply_markup=get_keyboard_fab("long_ma"))

    #   send_message = """Введите сообщение в виде /set long_ma; short_ma; std. \n
    #    Например: /set 15; 3; 5"""  

    #   await message.answer(send_message)

@dp.message_handler(lambda message: message.text == "short_ma")
async def sittings_setup(message: types.Message):

    user_value = user_data["short_ma"]
    
    await message.answer(f"Укажите значение short_ma: {user_value}", reply_markup=get_keyboard_fab("short_ma"))

@dp.message_handler(lambda message: message.text == "std_period")
async def sittings_setup(message: types.Message):

    user_value = user_data["std_period"]
    
    await message.answer(f"Укажите значение std_period: {user_value}", reply_markup=get_keyboard_fab("std_period"))



@dp.message_handler(commands="set")
async def set(message: types.Message):
    
    global long_ma
    global short_ma
    global std_period


    m_message = message.text.split(sep=";")

    long_ma = m_message[0].split()[1]
    short_ma = m_message[1]
    std_period = m_message[2]       
    
    await message.answer(f"""Установлены настройки робота \n
    long_ma: {long_ma}    \n
    short_ma: {short_ma}     \n
    std_period: {std_period}   \n
    """)

@dp.message_handler(lambda message: message.text == "Инструкция")
async def show_help(message: types.Message):

    await message.answer(help)



@dp.errors_handler(exception=BotBlocked)
async def error_bot_blocked(update: types.Update, exception: BotBlocked):
    # Update: объект события от Telegram. Exception: объект исключения
    # Здесь можно как-то обработать блокировку, например, удалить пользователя из БД
    print(f"Меня заблокировал пользователь!\nСообщение: {update}\nОшибка: {exception}")

    # Такой хэндлер должен всегда возвращать True,
    # если дальнейшая обработка не требуется.
    return True

@dp.errors_handler(exception=NetworkError)
async def error_Network_Error(update: types.Update, exception: NetworkError):
    # Update: объект события от Telegram. Exception: объект исключения
    # Здесь можно как-то обработать блокировку, например, удалить пользователя из БД
    print(f"ClientConnectorError: Cannot connect to host api.telegram.org:443 ssl:default [None] \nСообщение: {update}\nОшибка: {exception}")

    # Такой хэндлер должен всегда возвращать True,
    # если дальнейшая обработка не требуется.
    return True


if __name__ == "__main__":
    # Запуск бота
    executor.start_polling(dp, skip_updates=True)
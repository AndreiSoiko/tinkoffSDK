import logging
from aiogram import Bot, Dispatcher, executor, types
import os
from aiogram.utils.exceptions import BotBlocked
from numpy import std
import my_moving_average
import robot_fatbold


BOT_TOKEN = os.environ["INVEST_BOT_TOKEN"]                             
password = os.environ["INVEST_BOT_PASSWORD"]               

status_trade_robot = False #Глобальная переменная для хранения статуса робота.
robot_must_work = True #Глобальная переменная для остановки робота

# Объект бота
bot = Bot(token = BOT_TOKEN)
# Диспетчер для бота
dp = Dispatcher(bot)
# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)

help = """
/help - показывает подсказку 
/set - устанавливает настройки
сообщение "Запустить торгового робота" запускает робота с настройками, которые ты задал или настройками по умолчанию
сообщение "Остановить торгового робота" останавливает робота
сообщение "Настроить" показывает способ задать настройки

Робот работает по стратегии:
 short_ma > long_ma открывает позицию
 short_ma < long_ma продает акции


"""


long_ma = 15
short_ma = 3
std_period = 5

@dp.message_handler(commands="start")
async def cmd_start(message: types.Message):
    
    await message.answer("Введите пароль")
    
    
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


    
@dp.message_handler(lambda message: message.text == "Запустить торгового робота")
async def start_trade(message: types.Message):
    
    global status_trade_robot
    global robot_must_work

    if status_trade_robot == False: 

        status = "Working"

        gen = robot_fatbold.main(long_ma=long_ma,short_ma=short_ma,std_period=std_period)

        flag = True #Чтобы один раз сообщить, что робот запущен.

        while status ==  "Working" and robot_must_work:
            response = await gen.__anext__()
            status = response['status'] 
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
                status_trade_robot = True
                robot_must_work = True

            #status = response['status']
            #Робот работает ничего не делаем
        
        status_trade_robot = False #Изменим статус
        robot_must_work = True #Поднимим флаг, чтобы робот мог запуститься
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
        
    elif status_trade_robot == True:
        await message.answer("Робот уже запущен") 
    else:
        await message.answer("Робот в непонятном состоянии") 



@dp.message_handler(lambda message: message.text == "Остановить торгового робота")
async def stop_trade(message: types.Message):

    global status_trade_robot
    global robot_must_work

    if status_trade_robot == True: 
        robot_must_work = False #Глобальная переменная для остановки робота
    else:        
        await message.answer("Робот и так не работал")

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
      send_message = """Введите сообщение в виде /set long_ma; short_ma; std. \n
       Например: /set 15; 3; 5"""  

      await message.answer(send_message)



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



@dp.errors_handler(exception=BotBlocked)
async def error_bot_blocked(update: types.Update, exception: BotBlocked):
    # Update: объект события от Telegram. Exception: объект исключения
    # Здесь можно как-то обработать блокировку, например, удалить пользователя из БД
    print(f"Меня заблокировал пользователь!\nСообщение: {update}\nОшибка: {exception}")

    # Такой хэндлер должен всегда возвращать True,
    # если дальнейшая обработка не требуется.
    return True


if __name__ == "__main__":
    # Запуск бота
    executor.start_polling(dp, skip_updates=True)
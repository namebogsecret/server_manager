from aiogram import types
from system_controller import SystemController
from df import get_disk_usage_percent
#from aiogram.dispatcher.filters.state import State, StatesGroup
import os
from dotenv import load_dotenv
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

load_dotenv()
users_string = os.getenv("USERS")
ALLOWED_USERS = users_string.split(",") if users_string else []
services_string = os.getenv("SERVICES")
services = services_string.split(",") if services_string else []
# class BotStates(StatesGroup):
#     home = State()
#     service_management = State()
#     # Динамически создаем состояния для каждого сервиса
#     for service in services:
#         vars()[service] = State()

def get_main_menu_keyboard():
    keyboard = InlineKeyboardMarkup()
    
    #keyboard.add(InlineKeyboardButton("Статус", callback_data="status"))
    keyboard.add(InlineKeyboardButton("Загрузка CPU", callback_data="cpu_load"))
    keyboard.add(InlineKeyboardButton("Свободное место", callback_data="disk_usage"))
    keyboard.add(InlineKeyboardButton("Список всех сервисов", callback_data="services"))
    keyboard.add(InlineKeyboardButton("Сервисы работают", callback_data="services_up"))
    keyboard.add(InlineKeyboardButton("Управление сервисами", callback_data="service_management"))
    keyboard.add(InlineKeyboardButton("Убить телеграм", callback_data="kill_telegram"))
    keyboard.add(InlineKeyboardButton("Получить id", callback_data="get_user_id"))
    keyboard.add(InlineKeyboardButton("Перезагрузить", callback_data="reboot"))
    keyboard.add(InlineKeyboardButton("Помощь", callback_data="help"))
    return keyboard

def get_service_choose_keyboard():
    keyboard = InlineKeyboardMarkup()
    #services = ["nginx", "apache", "mysql"]  # Пример списка сервисов
    for service in services:
        keyboard.add(InlineKeyboardButton(service, callback_data=f"service__{service}"))
    keyboard.add(InlineKeyboardButton("Назад", callback_data="back_to_home"))
    return keyboard

def get_service_keyboard(service_name, is_running):
    if service_name not in services:
        return None
    keyboard = InlineKeyboardMarkup()
    #проверка запущен сервис или нет
    if is_running:
        keyboard.add(InlineKeyboardButton("Перезапустить", callback_data=f"restart__{service_name}"))
        keyboard.add(InlineKeyboardButton("Остановить", callback_data=f"stop__{service_name}"))
    else:
        keyboard.add(InlineKeyboardButton("Запустить", callback_data=f"start__{service_name}"))
    keyboard.add(InlineKeyboardButton("Информация", callback_data=f"info__{service_name}"))
    keyboard.add(InlineKeyboardButton("Назад", callback_data="service_management"))
    keyboard.add(InlineKeyboardButton("Домой", callback_data="back_to_home"))
    return keyboard


def is_list(obj):
    return isinstance(obj, list)

async def start_command_handler(message: types.Message):
    # если нужно будет удалить клавиатуру
    # keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    # # Добавляем кнопку с текстом /start
    # keyboard.add(types.KeyboardButton("/start"))
    # await message.answer("Нажмите на кнопку, чтобы начать", reply_markup=keyboard)
    #await message.answer("Клавиатура удалена.", reply_markup=types.ReplyKeyboardRemove())
    if str(message.from_user.id) not in ALLOWED_USERS:
        await not_allowed(message)
        return
    # Создание клавиатуры
    keyboard = get_main_menu_keyboard()
    
    # Отправка сообщения с клавиатурой
    await message.answer("Что делаем?", reply_markup=keyboard)


async def callback_query_handler(query: types.CallbackQuery, state: FSMContext):
    if str(query.from_user.id) not in ALLOWED_USERS:
        await not_allowed(query.message)
        return
    controller = SystemController()
    data = query.data
    get_main_menu_keyboard()
    if data.startswith("service_management"):

        keyboard = get_service_choose_keyboard()
        await query.message.answer("Выбери сервис:", reply_markup=keyboard)
    elif data.startswith("service__"):
        service_name = data.split("__")[1]
        if service_name in services:
            is_running = await controller.is_service_up(service_name)
            keyboard = get_service_keyboard(service_name, is_running)
            await query.message.answer(f"Управление сервисом {service_name}", reply_markup=keyboard)

    elif data.startswith("restart__"):
        service_name = data.split("__")[1]
        if service_name in services:
            await controller.restart_service_by_name(service_name)
            is_running = await controller.is_service_up(service_name)
            keyboard = get_service_keyboard(service_name, is_running)
            await query.message.answer(f"Сервис {service_name} перезапущен", reply_markup=keyboard)

    elif data.startswith("stop__"):
        service_name = data.split("__")[1]
        if service_name in services:
            await controller.stop_and_disable_service_by_name(service_name)
            is_running = await controller.is_service_up(service_name)
            keyboard = get_service_keyboard(service_name, is_running)
            await query.message.answer(f"Сервис {service_name} остановлен", reply_markup=keyboard)

    elif data.startswith("start__"):
        service_name = data.split("__")[1]
        if service_name in services:
            await controller.start_and_enable_service_by_name(service_name)
            is_running = await controller.is_service_up(service_name)
            keyboard = get_service_keyboard(service_name, is_running)
            await query.message.answer(f"Сервис {service_name} запущен", reply_markup=keyboard)

    elif data.startswith("info__"):
        service_name = data.split("__")[1]
        if service_name in services:
            is_running = await controller.is_service_up(service_name)
            keyboard = get_service_keyboard(service_name, is_running)
            await query.message.answer(await controller.get_service_info(service_name), reply_markup=keyboard)
    elif data == "back_to_home":
        keyboard = get_main_menu_keyboard()
        await query.message.answer("Что делаем?", reply_markup=keyboard)
    elif data == "reboot":
        await query.message.answer("Перезагрузка...", reply_markup=get_main_menu_keyboard())
        controller.reboot_computer()
    # elif data == "status":
    #     pass
    elif data == "cpu_load":
        result = await controller.check_cpu_load_by_this_services()
        result = dict_to_str(result, controller)
        result = f"{await controller.total_cpu_load()}\n{dict_to_str(await controller.top_cpu(), controller)}\n{result}"
        await query.message.answer(result, reply_markup=get_main_menu_keyboard())
    elif data == "services_up":
        result = await controller.check_what_services_are_up()
        result = list_to_str(result, controller)
        await query.message.answer(result, reply_markup=get_main_menu_keyboard())
    elif data == "services":
        result = await controller.print_all_services()
        result = list_to_str(result, controller)
        await query.message.answer(result, reply_markup=get_main_menu_keyboard())
    elif data == "kill_telegram":
        await query.message.answer(await controller.find_and_kill("telegram"), reply_markup=get_main_menu_keyboard())
    elif data == "get_user_id":
        await query.message.answer(str(query.from_user.id), reply_markup=get_main_menu_keyboard())
    elif data == "service_management":
        keyboard = get_service_choose_keyboard()
        await query.message.answer("Выберите сервис", reply_markup=keyboard)
    elif data == "disk_usage":
        await query.message.answer(await get_disk_usage_percent(), reply_markup=get_main_menu_keyboard())
    elif data == "help":
        #query.message.answer("Вызвана помощь")
        await query.message.answer(await get_help_message(), reply_markup=get_main_menu_keyboard())

    await query.answer()

async def service_management_handler(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    service_name = user_data.get("service_name")
    if service_name:
        # Отправляем сообщение или клавиатуру для управления сервисом
        # Например, "Управление сервисом: {service_name}"
        pass


def is_dict(obj):
    return isinstance(obj, dict)

def list_to_str(my_list, controller, true_index = False):
    text = ""
    for index, item in enumerate(my_list, start=1):
        if true_index:
            index = controller.services.index(item) + 1
        text += f"{index}. {item}\n"
    return text

def dict_to_str(my_dict, controller, true_index = False):
    text = ""
    for index, (key, value) in enumerate(my_dict.items(), start=1):
        if true_index:
            index = controller.services.index(key) + 1
        text += f"{index}. {key}: {value}\n"
    return text

async def handle_reboot(message, controller):
    await controller.reboot_computer()

async def handle_service_action(message, controller, action):
    """ Обрабатывает действия с сервисами: перезапуск, остановка и запуск. """
    try:
        service_number = int(message.text.split(' ')[1]) - 1
        await action(service_number)
    except (ValueError, IndexError):
        await message.answer("Неправильный номер сервиса")
        return True  # Возвращаем True, чтобы указать на ошибку

async def gpt_chat(message: types.Message):
    if str(message.from_user.id) not in ALLOWED_USERS:
        await not_allowed(message)
        return
    controller = SystemController()

    async def reboot():
        await handle_reboot(message, controller)

    async def restart_service():
        await handle_service_action(message, controller, controller.restart_service)

    async def stop_service():
        await handle_service_action(message, controller, controller.stop_and_disable_service)

    async def start_service():
        await handle_service_action(message, controller, controller.start_and_enable_service)

    async def check_disk_usage():
        return await get_disk_usage_percent()

    async def check_services_up():
        return await controller.check_what_services_are_up()

    async def check_cpu_load():
        return await controller.check_cpu_load_by_this_services()

    async def help_message():
        return await get_help_message()
    
    async def print_all_services():
        return await controller.print_all_services()

    async def kill_telegram():
        return await controller.find_and_kill("telegram")
    
    async def get_id():
        return str(message.from_user.id)

    commands = {
        "///перезагрузить": reboot,
        "///перезапустить": restart_service,
        "///остановить": stop_service,
        "///запустить": start_service,
        "///свободно": check_disk_usage,
        "///работают": check_services_up,
        "///загрузка": check_cpu_load,
        "///сервисы": print_all_services,
        "///убить": kill_telegram,
        "///get_user_id": get_id,
        "///помощь": help_message
    }

    command = commands.get(message.text.split(' ')[0])
    if command:
        result = await command()
        if result is not True:  # Если не было ошибки в обработке сервиса
            if is_list(result):
                result = list_to_str(result, controller, True)
            elif is_dict(result):
                result = dict_to_str(result, controller, True)
                result = f"{await controller.total_cpu_load()}\n{dict_to_str(await controller.top_cpu(), controller)}\n{result}"
            await message.answer(result if result else "Выполнено")
    else:
        await message.answer("Я не знаю такой команды")


async def get_help_message():
    return ("///перезагрузить - перезагрузить компьютер\n" +
            "///перезагрузить [номер] - перезагрузить сервис по номеру\n" +
            "///остановить [номер] - остановить сервис по номеру\n" +
            "///запустить [номер] - запустить сервис по номеру\n" +
            "///работают - напечатать работающие сервисы\n" +
            "///свободно - свободно места на диске\n" +
            "///загрузка - уровень загрузки каждым сервисом\n" +
            "///помощь - вывести это сообщение")

async def get_help_message_str():
    return str("///перезагрузить - перезагрузить компьютер\n" +
            "///перезагрузить [номер] - перезагрузить сервис по номеру\n" +
            "///остановить [номер] - остановить сервис по номеру\n" +
            "///запустить [номер] - запустить сервис по номеру\n" +
            "///работают - напечатать работающие сервисы\n" +
            "///свободно - свободно места на диске\n" +
            "///загрузка - уровень загрузки каждым сервисом\n" +
            "///помощь - вывести это сообщение")
async def not_allowed(message: types.Message):
    with open("/root/myservermanager/not_allowed.txt", "a") as f:
        f.write(f"{message.from_user.id}: {message.text}\n")
    await message.answer(f"Вы не имеете доступа к этому боту")

async def voice_to_text(message: types.Message):
    if message.from_user.id not in ALLOWED_USERS:
        await not_allowed(message)
        return
    await message.answer("Пока не реализовано")

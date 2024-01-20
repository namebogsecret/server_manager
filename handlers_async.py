from aiogram import types
from system_controller import SystemController
from df import get_disk_usage_percent
from aiogram.dispatcher.filters.state import State, StatesGroup
import os
from dotenv import load_dotenv
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

load_dotenv()
users_string = os.getenv("USERS")
ALLOWED_USERS = users_string.split(",") if users_string else []
services_string = os.getenv("SERVICES")
services = services_string.split(",") if services_string else []
class BotStates(StatesGroup):
    home = State()
    service_management = State()
    # Динамически создаем состояния для каждого сервиса
    for service in services:
        vars()[service] = State()

def get_main_menu_keyboard():
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("Перезагрузить", callback_data="reboot"))
    keyboard.add(InlineKeyboardButton("Статус", callback_data="status"))
    keyboard.add(InlineKeyboardButton("Помощь", callback_data="help"))
    return keyboard

def get_service_management_keyboard():
    keyboard = InlineKeyboardMarkup()
    services = ["nginx", "apache", "mysql"]  # Пример списка сервисов
    for service in services:
        keyboard.add(InlineKeyboardButton(service, callback_data=f"service_{service}"))
    return keyboard



def is_list(obj):
    return isinstance(obj, list)

async def callback_query_handler(query: types.CallbackQuery, state: FSMContext):
    data = query.data

    if data.startswith("service_"):
        service_name = data.split("_")[1]
        await state.update_data(service_name=service_name)  # Сохраняем выбранный сервис
        await BotStates.service_management.set()  # Устанавливаем состояние управления сервисами
        # Отправляем клавиатуру или сообщение для управления выбранным сервисом
    elif data == "back_to_home":
        await BotStates.home.set()  # Возвращаемся в начальное состояние
    elif data == "reboot":
        # Выполнить действие "Перезагрузить"
        pass
    elif data == "status":
        # Выполнить действие "Статус"
        pass
    elif data == "help":
        # Показать сообщение помощи
        pass

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

async def not_allowed(message: types.Message):
    with open("/root/myservermanager/not_allowed.txt", "a") as f:
        f.write(f"{message.from_user.id}: {message.text}\n")
    await message.answer(f"Вы не имеете доступа к этому боту")

async def voice_to_text(message: types.Message):
    if message.from_user.id not in ALLOWED_USERS:
        await not_allowed(message)
        return
    await message.answer("Пока не реализовано")

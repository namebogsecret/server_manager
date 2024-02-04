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

def all_servers_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=2)
    buttons = [
        InlineKeyboardButton("Сервер 1", callback_data="server1"),
        InlineKeyboardButton("Сервер 2", callback_data="server2")
    ]
    keyboard.add(*buttons)
    return keyboard

def get_main_menu_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=2)  # Задаем ширину ряда равной 2

    buttons = [
        InlineKeyboardButton("Статистика", callback_data="statistica"),
        InlineKeyboardButton("Управление сервисами", callback_data="service_management"),
        InlineKeyboardButton("Убить процессы", callback_data="kill"),
        InlineKeyboardButton("Crone", callback_data="crone"),
        InlineKeyboardButton("Помощь", callback_data="help")
    ]

    keyboard.add(*buttons)  # Добавляем кнопки в клавиатуру
    keyboard.row(
        InlineKeyboardButton("Ко всем серверам", callback_data="to_all_servers")
    )
    return keyboard

def crone_keyboard(cron_jobs):
    keyboard = InlineKeyboardMarkup(row_width=2)  # Задаем ширину ряда равной 2
    # buttons= [
    # for index, kej, status in enumerate(cron_jobs, start=1):

    #     InlineKeyboardButton(f"{index}. {kej} - {status}", callback_data=f"crone__{kej}")
        
    # ]
    buttons = []
    for kej, active in cron_jobs.items():
        status = "✅" if active else "❌"
        buttons.append(InlineKeyboardButton(f"{status} {kej}", callback_data=f"crone-{kej}"))
    keyboard.add(*buttons)
    keyboard.row(
        InlineKeyboardButton("Назад", callback_data="back_to_home")
    )

    #keyboard.add(*buttons)  # Добавляем кнопки в клавиатуру
    return keyboard

def statistica_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=2)  # Задаем ширину ряда равной 2

    buttons = [
        InlineKeyboardButton("Загрузка CPU", callback_data="cpu_load"),
        InlineKeyboardButton("Загрузка памяти", callback_data="mem_usage"),
        InlineKeyboardButton("Свободное место", callback_data="disk_usage"),
        InlineKeyboardButton("Получить id", callback_data="get_user_id"),
        InlineKeyboardButton("Назад", callback_data="back_to_home")
    ]

    keyboard.add(*buttons)  # Добавляем кнопки в клавиатуру
    return keyboard

def killing_processes_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=2)  # Задаем ширину ряда равной 2

    buttons = [
        InlineKeyboardButton("Убить телеграм", callback_data="kill_telegram"),
        InlineKeyboardButton("Убить vscode", callback_data="kill_vscode"),
        InlineKeyboardButton("Перезагрузить", callback_data="reboot"),
        InlineKeyboardButton("Назад", callback_data="back_to_home")
    ]

    keyboard.add(*buttons)  # Добавляем кнопки в клавиатуру
    return keyboard

def get_service_choose_keyboard():

    keyboard = InlineKeyboardMarkup(row_width=2)  # Устанавливаем ширину ряда равной 2
    keyboard.row(
        #InlineKeyboardButton("Список всех сервисов", callback_data="services"),
        InlineKeyboardButton("Запущенные сервисы", callback_data="services_up")
    )
    # Добавляем кнопки для сервисов парами
    for i in range(0, len(services), 2):
        if i + 1 < len(services):
            # Если есть следующий элемент, добавляем две кнопки в ряд
            keyboard.row(
                InlineKeyboardButton(f"{i+1}. {services[i]}", callback_data=f"service__{services[i]}"),
                InlineKeyboardButton(f"{i+2}. {services[i + 1]}", callback_data=f"service__{services[i + 1]}")
            )
        else:
            # Если это последний элемент и он один, добавляем одну кнопку в ряд
            keyboard.row(
                InlineKeyboardButton(f"{i+1}. {services[i]}", callback_data=f"service__{services[i]}")
            )

    # Добавляем кнопку "Назад" в отдельный ряд
    keyboard.row(
        InlineKeyboardButton("Назад", callback_data="back_to_home")
    )

    return keyboard

def get_service_keyboard(service_name, is_running):
    if service_name not in services:
        return None

    keyboard = InlineKeyboardMarkup(row_width=2)  # Устанавливаем ширину ряда равной 2

    # Проверка, запущен ли сервис
    if is_running:
        if service_name == "my_server_manager":
            keyboard.row(
                InlineKeyboardButton("Перезапустить", callback_data=f"restart__{service_name}")
            )
        else:
            keyboard.row(
                InlineKeyboardButton("Перезапустить", callback_data=f"restart__{service_name}"),
                InlineKeyboardButton("Остановить", callback_data=f"stop__{service_name}")
            )
    else:
        keyboard.row(
            InlineKeyboardButton("Запустить", callback_data=f"start__{service_name}")
        )

    keyboard.row(
        InlineKeyboardButton("Информация", callback_data=f"info__{service_name}"),
        InlineKeyboardButton("Назад", callback_data="service_management")
    )

    keyboard.row(
        InlineKeyboardButton("Назад к серверу", callback_data="back_to_home")
    )

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
    keyboard = all_servers_keyboard()
    
    # Отправка сообщения с клавиатурой
    await message.answer("Выберите сервер:", reply_markup=keyboard)


async def callback_query_handler(query: types.CallbackQuery, state: FSMContext):
    if str(query.from_user.id) not in ALLOWED_USERS:
        await not_allowed(query.message)
        return
    controller = SystemController()
    data = query.data
    #get_main_menu_keyboard()
    if data.startswith("service_management"):
        await query.message.edit_reply_markup(reply_markup=None)
        keyboard = get_service_choose_keyboard()
        await query.message.answer("Выбери сервис:", reply_markup=keyboard)
    elif data == "to_all_servers":
        await query.message.edit_reply_markup(reply_markup=None)
        keyboard = all_servers_keyboard()
        await query.message.answer("Выберите сервер:", reply_markup=keyboard)
    elif data.startswith("server1"):
        await query.message.edit_reply_markup(reply_markup=None)
        await query.message.answer("Вы на 1 сервере", reply_markup=get_main_menu_keyboard())
    elif data.startswith("service__"):
        await query.message.edit_reply_markup(reply_markup=None)
        service_name = data.split("__")[1]
        if service_name in services:
            is_running = await controller.is_service_up(service_name)
            keyboard = get_service_keyboard(service_name, is_running)
            await query.message.answer(f"Управление сервисом {service_name}", reply_markup=keyboard)

    elif data.startswith("restart__"):
        await query.message.edit_reply_markup(reply_markup=None)
        service_name = data.split("__")[1]
        if service_name in services:
            if service_name == "my_server_manager":
                await query.message.answer(f"Перезагружаю", reply_markup=get_main_menu_keyboard())
                await controller.restart_service_by_name(service_name)
                return
            await controller.restart_service_by_name(service_name)
            is_running = await controller.is_service_up(service_name)
            keyboard = get_service_keyboard(service_name, is_running)
            await query.message.answer(f"Сервис {service_name} перезапущен", reply_markup=keyboard)

    elif data.startswith("stop__"):
        await query.message.edit_reply_markup(reply_markup=None)
        service_name = data.split("__")[1]
        if service_name in services:
            await controller.stop_and_disable_service_by_name(service_name)
            is_running = await controller.is_service_up(service_name)
            keyboard = get_service_keyboard(service_name, is_running)
            await query.message.answer(f"Сервис {service_name} остановлен", reply_markup=keyboard)

    elif data.startswith("start__"):
        await query.message.edit_reply_markup(reply_markup=None)
        service_name = data.split("__")[1]
        if service_name in services:
            await controller.start_and_enable_service_by_name(service_name)
            is_running = await controller.is_service_up(service_name)
            keyboard = get_service_keyboard(service_name, is_running)
            await query.message.answer(f"Сервис {service_name} запущен", reply_markup=keyboard)

    elif data.startswith("info__"):
        await query.message.edit_reply_markup(reply_markup=None)
        service_name = data.split("__")[1]
        if service_name in services:
            is_running = await controller.is_service_up(service_name)
            keyboard = get_service_keyboard(service_name, is_running)
            await query.message.answer(await controller.get_service_info(service_name), reply_markup=keyboard)
    elif data == "back_to_home":
        await query.message.edit_reply_markup(reply_markup=None)
        keyboard = get_main_menu_keyboard()
        await query.message.answer("Что делаем?", reply_markup=keyboard)
    elif data == "reboot":
        await query.message.edit_reply_markup(reply_markup=None)
        await query.message.answer("Перезагрузка...", reply_markup=get_main_menu_keyboard())
        controller.reboot_computer()
    # elif data == "status":
    #     pass

    elif data == "kill":
        await query.message.edit_reply_markup(reply_markup=None)
        keyboard = killing_processes_keyboard()
        await query.message.answer("Что убиваем?", reply_markup=keyboard)

    elif data == "statistica":
        await query.message.edit_reply_markup(reply_markup=None)
        keyboard = statistica_keyboard()
        await query.message.answer("Что смотрим?", reply_markup=keyboard)
    
    elif data == "mem_usage":
        await query.message.edit_reply_markup(reply_markup=None)
        top_mem = await controller.top_mem_processes()
        top_mem = dict_to_str(top_mem, controller)
        result = await controller.check_memory_usage()

        await query.message.answer(f"Загрузка памяти:\n{result}\n{top_mem}", reply_markup=statistica_keyboard())

    elif data == "crone":
        await query.message.edit_reply_markup(reply_markup=None)
        cron_jobs = await controller.list_cron_jobs()
        keyboard = crone_keyboard(cron_jobs)
        await query.message.answer("Cron. Нажмите что бы включить/выключить", reply_markup=keyboard)

    elif data.startswith("crone-"):
        await query.message.edit_reply_markup(reply_markup=None)
        cron_job = data.split("-")[1]
        await controller.modify_cron_line(cron_job)
        cron_jobs = await controller.list_cron_jobs()
        keyboard = crone_keyboard(cron_jobs)
        await query.message.answer("Cron. Нажмите что бы включить/выключить", reply_markup=keyboard)

    elif data == "kill_vscode":
        await query.message.edit_reply_markup(reply_markup=None)
        await query.message.answer(f"Убито процессов vscode: {await controller.find_and_kill('vscode')}", reply_markup=killing_processes_keyboard())
    elif data == "cpu_load":
        await query.message.edit_reply_markup(reply_markup=None)
        result = await controller.check_cpu_load_by_this_services()
        result = dict_to_str(result, controller)
        result = f"Загрузка CPU:\n{await controller.total_cpu_load()}\n{dict_to_str(await controller.top_cpu(), controller)}\n{result}"
        await query.message.answer(result, reply_markup=statistica_keyboard())
    elif data == "services_up":
        await query.message.edit_reply_markup(reply_markup=None)
        result = await controller.check_what_services_are_up()
        result = list_to_str(result, controller)
        await query.message.answer(f"Запущенные сервисы:\n{result}", reply_markup=get_service_choose_keyboard())
    elif data == "services":
        await query.message.edit_reply_markup(reply_markup=None)
        result = await controller.print_all_services()
        result = list_to_str(result, controller)
        await query.message.answer(f"Список всех сервисов:\n{result}", reply_markup=get_main_menu_keyboard())
    elif data == "kill_telegram":
        await query.message.edit_reply_markup(reply_markup=None)
        await query.message.answer(f"Убито процессов телеграм: {await controller.find_and_kill('telegram')}", reply_markup=killing_processes_keyboard())
    elif data == "get_user_id":
        await query.message.edit_reply_markup(reply_markup=None)
        await query.message.answer(f"Curent User_id: {str(query.from_user.id)}", reply_markup=statistica_keyboard())
    elif data == "service_management":
        await query.message.edit_reply_markup(reply_markup=None)
        keyboard = get_service_choose_keyboard()
        await query.message.answer("Выберите сервис", reply_markup=keyboard)
    elif data == "disk_usage":
        await query.message.edit_reply_markup(reply_markup=None)
        await query.message.answer(f"На диске свободно: {100-int(await get_disk_usage_percent())} %", reply_markup=statistica_keyboard())
    elif data == "help":
        await query.message.edit_reply_markup(reply_markup=None)
        #query.message.answer("Вызвана помощь")
        await query.message.answer(await get_help_message_inline(), reply_markup=get_main_menu_keyboard())
    else:
        print("got to another server (from server1)")

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
    
    async def kill_something():
        try:
            process_name = message.text.split(' ')[1]
            return await controller.find_and_kill(process_name)
        except (ValueError, IndexError):
            await message.answer("Неправильное имя процесса")
            return True
    
    async def run_command():

        try:
            #убираем первое слово '///run_command ' пример '///run_command ls -la' -> 'ls -la'
            command = message.text.split(' ', 1)[1]
            return await controller.run_command(command)
        except (ValueError, IndexError):
            await message.answer("Неправильная команда")
            return True

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
        "///помощь": help_message,
        "///kill": kill_something,
        "///run_command": run_command
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

async def get_help_message_inline():
    return ("Этот бот умеет:\n" +
            "1. Проверять загрузку CPU\n" +
            "2. Проверять свободное место на диске\n" +
            "3. Показывать список всех сервисов\n" +
            "4. Показывать список работающих сервисов\n" +
            "5. Управлять сервисами:\n" +
            "   5.1. Перезапускать сервис\n" +
            "   5.2. Останавливать сервис\n" +
            "   5.3. Запускать сервис\n" +
            "   5.4. Показывает информацию о сервисе\n" +
            "6. Убивать процессы связанные с телеграм\n" +
            "7. Показывать id пользователя\n" +
            "8. Перезагружать компьютер\n" +
            "9. Показывать это сообщение\n"    
    )
async def not_allowed(message: types.Message):
    with open("/root/myservermanager/not_allowed.txt", "a") as f:
        f.write(f"{message.from_user.id}: {message.text}\n")
    await message.answer(f"Вы не имеете доступа к этому боту")

async def voice_to_text(message: types.Message):
    if message.from_user.id not in ALLOWED_USERS:
        await not_allowed(message)
        return
    await message.answer("Пока не реализовано")

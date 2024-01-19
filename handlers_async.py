from aiogram import types
from system_controller import SystemController
from df import get_disk_usage_percent
from aiogram.dispatcher.filters.state import State, StatesGroup

class Form(StatesGroup):
    home = State()  # Домашнее состояние
    restart = State()  # Перезапустить
    stop = State()  # Остановить
    start = State()  # Запустить

async def handle_reboot(message, controller):
    await controller.reboot_computer()

async def handle_service_action(message, controller, action):
    """ Обрабатывает действия с сервисами: перезапуск, остановка и запуск. """
    try:
        service_number = int(message.text.split(' ')[1]) + 1
        await action(service_number)
    except (ValueError, IndexError):
        await message.answer("Неправильный номер сервиса")
        return True  # Возвращаем True, чтобы указать на ошибку

async def gpt_chat(message: types.Message):
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

    commands = {
        "///перезагрузить": reboot,
        "///перезапустить": restart_service,
        "///остановить": stop_service,
        "///запустить": start_service,
        "///свободно": check_disk_usage,
        "///работают": check_services_up,
        "///загрузка": check_cpu_load,
        "///помощь": help_message
    }

    command = commands.get(message.text.split(' ')[0])
    if command:
        result = await command()
        if result is not True:  # Если не было ошибки в обработке сервиса
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


async def voice_to_text(message: types.Message):
    await message.answer("Пока не реализовано")

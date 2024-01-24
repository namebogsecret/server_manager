import subprocess
import os
from dotenv import load_dotenv
import psutil
import re

class SystemController:
    def __init__(self):
        load_dotenv()
        services_string = os.getenv("SERVICES")
        self.services = services_string.split(",") if services_string else []
        
    async def print_all_services(self):
        return self.services

    async def reboot_computer(self):
        """ Перезагружает компьютер. """
        subprocess.run(["sudo", "reboot"], check=True)

    async def restart_service_by_name(self, service_name):
        """
        Перезагружает один из трех сервисов.
        :param service_name: Название сервиса.
        """
        subprocess.run(["sudo", "systemctl", "restart", service_name], check=True)

    async def restart_service(self, service_number):
        """
        Перезагружает один из трех сервисов.
        :param service_number: Номер сервиса (0, 1, 2).
        """
        if service_number in range(len(self.services)):
            service_name = self.services[service_number]
            await self.restart_service_by_name(service_name)
        else:
            raise ValueError("Неправильный номер сервиса")
        
    async def stop_and_disable_service_by_name(self, service_name):
        """
        Останавливает и отключает один из трех сервисов.
        :param service_name: Название сервиса.
        """
        subprocess.run(["sudo", "systemctl", "stop", service_name], check=True)
        subprocess.run(["sudo", "systemctl", "disable", service_name], check=True)

    async def stop_and_disable_service(self, service_number):
        """
        Останавливает и отключает один из трех сервисов.
        :param service_number: Номер сервиса (0, 1, 2).
        """
        if service_number in range(len(self.services)):
            service_name = self.services[service_number]
            await self.stop_and_disable_service_by_name(service_name)
        else:
            raise ValueError("Неправильный номер сервиса")
        
    async def start_and_enable_service_by_name(self, service_name):
        """
        Запускает и включает один из трех сервисов.
        :param service_name: Название сервиса.
        """
        subprocess.run(["sudo", "systemctl", "start", service_name], check=True)
        subprocess.run(["sudo", "systemctl", "enable", service_name], check=True)

    async def start_and_enable_service(self, service_number):
        """
        Запускает и включает один из трех сервисов.
        :param service_number: Номер сервиса (0, 1, 2).
        """
        if service_number in range(len(self.services)):
            service_name = self.services[service_number]
            await self.start_and_enable_service_by_name(service_name)
        else:
            raise ValueError("Неправильный номер сервиса")

    async def is_service_up(self, service_name):
        """
        Проверяет, запущен ли сервис.
        :param service_name: Название сервиса.
        """
        try:
            subprocess.run(["sudo", "systemctl", "is-active", service_name], check=True)
            return True
        except subprocess.CalledProcessError:
            return False

    async def get_service_info(self, service_name):
        """
        Возвращает информацию о сервисе.
        :param service_name: Название сервиса.
        """
        try:
            output = subprocess.check_output(
                ["systemctl", "show", service_name], text=True
            )
            return f"Информация о сервисе {service_name}:\n{output.strip()[:400]}"
        except subprocess.CalledProcessError:
            return "Сервис не найден"

    async def check_what_services_are_up(self):
        up_services = []
        for service in self.services:
            if await self.is_service_up(service):
                up_services.append(service)
        return up_services

    async def find_and_kill(self, pattern):
        killed = 0
        try:
            # Находим процессы, соответствующие шаблону
            result = subprocess.run(['pgrep', '-f', pattern], stdout=subprocess.PIPE, text=True)
            pids = result.stdout.strip().split('\n')

            for pid in pids:
                if pid:
                    # Убиваем каждый процесс по PID
                    subprocess.run(['kill', pid])
                    killed +=1
            return str(killed)
        except Exception as e:
            return f"Ошибка: {e} Killed {killed}"

    async def total_cpu_load(self):
        return psutil.cpu_percent(interval=1, percpu=True)
        #return psutil.cpu_percent(interval=5)

    async def top_cpu(self, n=5):
        # Запускаем команду и получаем вывод
        result = subprocess.run(['ps', '-eo', 'comm,%cpu', '--sort=-%cpu'], stdout=subprocess.PIPE, text=True)
        # Разбиваем вывод на строки и игнорируем первую (заголовок)
        lines = result.stdout.strip().split('\n')[1:]
        # Получаем первые n строк и создаем словарь
        process_cpu_dict = {}
        for line in lines[:n]:
            parts = line.split()
            process_name = ' '.join(parts[:-1])  # Название процесса может содержать пробелы
            cpu_load = parts[-1]  # Загрузка ЦПУ
            process_cpu_dict[process_name] = cpu_load

        return process_cpu_dict

    async def check_memory_usage(self):
        #free -h
        output = subprocess.check_output(
            ["free", "-h"], text=True
        )
        return output

    async def top_mem_processes(self, n=10):
        # Выполнение команды ps и получение вывода
        output = subprocess.check_output(
            ["ps", "aux", "--sort=-%mem"], text=True
        )
        lines = output.strip().split('\n')[1:]  # Пропускаем первую строку (заголовки)
        process_mem_dict = {}
        lines = lines[:n]
        for line in lines:
            # Разделяем строку с помощью регулярного выражения
            parts = re.split(r'\s+', line, maxsplit=10)
            # Получаем первые 20 символов названия процесса
            process_name = parts[-1][:20] + parts[-1][-10:]
            mem_usage = parts[3]
            process_mem_dict[process_name] = mem_usage

        return process_mem_dict
    
    async def check_cpu_load_by_this_services(self):
        services_are_up = await self.check_what_services_are_up()
        cpu_load_by_service = {}
        #global cpu load

        for service in services_are_up:
            try:
                # # Получение PID'ов процессов, связанных с сервисом
                # pids = subprocess.check_output(
                #     ["pidof", service], text=True
                # ).strip().split()

                # total_cpu_load = 0
                # for pid in pids:
                #     # Использование команды ps для получения загрузки ЦПУ каждым PID
                #     output = subprocess.check_output(
                #         ["ps", "-p", pid, "-o", "%cpu"], text=True
                #     )
                #     # Предполагаем, что вывод содержит заголовок и значение
                #     cpu_load = float(output.splitlines()[1].strip())
                #     total_cpu_load += cpu_load
                
                # cpu_load_by_service[service] = total_cpu_load
                # Получение PID'а главного процесса сервиса
                output = subprocess.check_output(
                    ["systemctl", "show", "-p", "MainPID", service], text=True
                )
                pid = output.strip().split("=")[1]
                if pid != "0":  # Если PID не 0, то сервис запущен
                    # Получение загрузки ЦПУ этим PID
                    cpu_load_output = subprocess.check_output(
                        ["ps", "-p", pid, "-o", "%cpu"], text=True
                    )
                    cpu_load = float(cpu_load_output.splitlines()[1].strip())
                    cpu_load_by_service[service] = cpu_load
            except subprocess.CalledProcessError as er:
                print(er)
                pass
            

        return cpu_load_by_service
    
    async def _get_current_crontab(self):
        """ Получает текущий crontab пользователя """
        try:
            return subprocess.check_output(['crontab', '-l'], stderr=subprocess.STDOUT).decode()
        except subprocess.CalledProcessError:
            # Возвращает пустую строку, если у пользователя нет задач в crontab
            return ""

    async def list_cron_jobs(self):
        current_crontab = await self._get_current_crontab()
        lines = current_crontab.splitlines()
        dict_cron_jobs = {}
        for line in lines:
            if line.strip():
                active = False if line.strip().startswith("#") else True
                command_part = line.strip().split()[-1].split('/')[-1]
                #print(f"{status}: {command_part}")
                dict_cron_jobs[command_part] = active
        return dict_cron_jobs

    async def _write_new_crontab(self, new_crontab):
        """ Записывает новый crontab """
        process = subprocess.Popen(['crontab', '-'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        process.communicate(new_crontab.encode())

    async def modify_cron_line(self, service_name):
        current_crontab = await self._get_current_crontab()
        lines = current_crontab.splitlines()
        modified_lines = []

        for line in lines:
            if re.search(r'\b' + re.escape(service_name) + r'\b', line):
                if not line.strip().startswith("#"):
                    line = "#" + line
                elif line.strip().startswith("#"):
                    line = line[1:]
            modified_lines.append(line)

        await self._write_new_crontab('\n'.join(modified_lines)+"\n")

# Пример использования:
#controller = SystemController()
# controller.reboot_computer()  # Раскомментируйте для перезагрузки компьютера
# controller.restart_service(0)  # Перезагружает первый сервис

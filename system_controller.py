import subprocess
import os
from dotenv import load_dotenv

class SystemController:
    def __init__(self):
        load_dotenv()
        services_string = os.getenv("SERVICES")
        self.services = services_string.split(",") if services_string else []
        
    async def reboot_computer(self):
        """ Перезагружает компьютер. """
        subprocess.run(["sudo", "reboot"], check=True)

    async def restart_service(self, service_number):
        """
        Перезагружает один из трех сервисов.
        :param service_number: Номер сервиса (0, 1, 2).
        """
        if service_number in range(len(self.services)):
            service_name = self.services[service_number]
            subprocess.run(["sudo", "systemctl", "restart", service_name], check=True)
        else:
            raise ValueError("Неправильный номер сервиса")
        
    async def stop_and_disable_service(self, service_number):
        """
        Останавливает и отключает один из трех сервисов.
        :param service_number: Номер сервиса (0, 1, 2).
        """
        if service_number in range(len(self.services)):
            service_name = self.services[service_number]
            subprocess.run(["sudo", "systemctl", "stop", service_name], check=True)
            subprocess.run(["sudo", "systemctl", "disable", service_name], check=True)
        else:
            raise ValueError("Неправильный номер сервиса")
        
    async def start_and_enable_service(self, service_number):
        """
        Запускает и включает один из трех сервисов.
        :param service_number: Номер сервиса (0, 1, 2).
        """
        if service_number in range(len(self.services)):
            service_name = self.services[service_number]
            subprocess.run(["sudo", "systemctl", "start", service_name], check=True)
            subprocess.run(["sudo", "systemctl", "enable", service_name], check=True)
        else:
            raise ValueError("Неправильный номер сервиса")

    async def check_what_services_are_up(self):
        up_services = []
        for service in self.services:
            try:
                subprocess.run(["sudo", "systemctl", "is-active", service], check=True)
                up_services.append(service)
            except subprocess.CalledProcessError:
                pass
        return up_services

    async def check_cpu_load_by_this_services(self):
        services_are_up = await self.check_what_services_are_up()
        cpu_load_by_service = {}
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
# Пример использования:
#controller = SystemController()
# controller.reboot_computer()  # Раскомментируйте для перезагрузки компьютера
# controller.restart_service(0)  # Перезагружает первый сервис

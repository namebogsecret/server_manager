import subprocess
import re

async def get_disk_usage_percent(mount_point = '/dev/sda1'):
    # Выполняем команду 'df' и получаем результат в виде строки
    result = subprocess.run(['df'], stdout=subprocess.PIPE).stdout.decode('utf-8')

    # Разделяем результат на строки
    lines = result.strip().split('\n')

    for line in lines:
        if mount_point in line:
            # Используем регулярное выражение для поиска процента использования
            match = re.search(r'\b(\d+)%', line)
            if match:
                # Возвращаем процент использования в виде числа
                return int(match.group(1))

    return None

if __name__ == '__main__':
    # Пример использования модуля
    disk_usage = get_disk_usage_percent('/dev/sda1')


import os
import multiprocessing
from utils import set_affinity

def get_cpu_count():
    """ Возвращает общее количество ядер процессора. """
    try:
        # Используем multiprocessing для получения количества доступных ядер
        return multiprocessing.cpu_count()
    except NotImplementedError:
        # Если multiprocessing не смог определить, используем os
        res = os.sysconf("SC_NPROCESSORS_ONLN")
        print(res)
        if res is not None:
            return res
        else:
            raise Exception("Не удалось определить количество ядер CPU")

if __name__ == '__main__':
    # Пример использования
    set_affinity([1])  # Привязываем процесс к первому ядру
    cpu_count = get_cpu_count()
    print(f"PID: {os.getpid()}")
    print(f"Общее количество ядер CPU: {cpu_count}")

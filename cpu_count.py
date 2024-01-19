import os
import multiprocessing
import os

def set_affinity(cores):
    """ Устанавливает аффинность (привязку) процесса к определенным ядрам. """
    pid = os.getpid()
    os.sched_setaffinity(pid, cores)
    print("done")

pid = os.getpid()  # Получаем PID текущего процесса
set_affinity(pid, [1])  # Привязываем процесс к первому ядру

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

  # Получаем PID текущего процесса
set_affinity([1])  # Привязываем процесс к первому ядру
print(pid)
print(1)
# Пример использования
cpu_count = get_cpu_count()
print(f"Общее количество ядер CPU: {cpu_count}")

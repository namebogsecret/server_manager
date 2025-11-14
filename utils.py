import os

def set_affinity(cores):
    """
    Устанавливает аффинность (привязку) процесса к определенным ядрам.

    Args:
        cores: список или set номеров ядер (например, [1] или {0, 1})
    """
    pid = os.getpid()
    os.sched_setaffinity(pid, cores)

import sys
import logging
import traceback
import inspect

if sys.argv[0].find('client') == -1:
    logger = logging.getLogger('server')
else:
    logger = logging.getLogger('client')


def log(func_to_log):
    """Функция-декоратор"""
    def log_saver(*args, **kwargs):
        """Обертка"""
        ret = func_to_log(*args, **kwargs)
        logger.debug(f'Была вызвана функция {func_to_log.__name__} c параметрами {args}, {kwargs}.\n'
                     f'Вызов из модуля {traceback.format_stack()[0].strip().split()[1]}.\n'
                     f'Вызов из функции {inspect.stack()[1][3]}.')
        return ret
    return log_saver

import threading
import os
import logging
import logging.handlers
from smlb.settings import LOG_DIR


_thread_locals = threading.local()


def set_current_user(user):
    _thread_locals.user=user


def get_current_user():
    return getattr(_thread_locals, 'user', None)


def get_logger_file(name, filename):
    logger = logging.getLogger(name)
    logging.basicConfig(level=logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - [%(funcName)s] - %(message)s')
    file_handler = logging.handlers.RotatingFileHandler(filename=os.path.join(LOG_DIR, filename),
                                                        maxBytes=10000000, backupCount=5)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    return logger



import logging.config
from datetime import datetime
import os

__PYGATT_LOG_LEVEL = "ERROR"


SC_LOGGING_CONF = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "simple": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        }
    },

    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "formatter": "simple",
            "stream": "ext://sys.stdout"
        },

        "info_file_handler": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "INFO",
            "formatter": "simple",
            "filename": "log/" + str(datetime.now().strftime("%Y-%m-%d-%H-%M-%S")) + "-info.log",
            "maxBytes": 10485760,
            "backupCount": 20,
            "encoding": "utf8"
        },

        "error_file_handler": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "ERROR",
            "formatter": "simple",
            "filename": "log/" + str(datetime.now().strftime("%Y-%m-%d-%H-%M-%S")) + "-error.log",
            "maxBytes": 10485760,
            "backupCount": 20,
            "encoding": "utf8"
        }
    },

    "loggers": {
        "my_module": {
            "level": "ERROR",
            "handlers": ["console"],
            "propagate": "no"
        }
    },

    "root": {
        "level": "INFO",
        "handlers": ["console", "info_file_handler", "error_file_handler"]
    }
}

def setup_logging(
        default_level = logging.INFO,
        env_key = 'LOG_CFG'
):
    """ Setup logging configuration"""
    try:
        path = os.path.abspath("log")
        log_folder = os.path.exists(path)
        if not log_folder:
            os.makedirs(path)
        logging.config.dictConfig(SC_LOGGING_CONF)
    except Exception as e:
        print(e)



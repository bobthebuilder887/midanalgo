import logging


def _init_logging(name: str = "sheet_log") -> logging.Logger:
    file_handler = logging.FileHandler("sheet_logs.log", encoding="utf-8", mode="w")
    format = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%H:%M:%S",
    )
    file_handler.setFormatter(format)

    sheet_log = logging.getLogger(name)
    sheet_log.setLevel(logging.INFO)
    sheet_log.addHandler(file_handler)

    return sheet_log


SHEET_LOG = _init_logging()

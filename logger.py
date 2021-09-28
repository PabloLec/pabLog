from os import access, X_OK
from pathlib import Path
from platform import system
from tempfile import gettempdir
from datetime import datetime
from errors import *
from colorama import Fore, Style


class Logger:
    _LEVELS = {"ERROR": 3, "WARNING": 2, "INFO": 1, "DEBUG": 0}

    def __init__(
        self, output_file: str = None, level: str = "INFO", enabled: bool = True
    ):
        self._output_file = (
            output_file
            if output_file is not None
            else Path(
                f"/tmp/{__name__}.log"
                if system() == "Darwin"
                else Path(gettempdir()) / f"{__name__}.log"
            )
        )
        level = level.upper()
        if level not in self._LEVELS:
            raise LogLevelDoesNotExist(level)
        self._level = level
        self._enabled = enabled

    @property
    def output_file(self):
        return self._output_file

    @output_file.setter
    def output_file(self, value):
        if value == "local":
            dir = Path(__file__).parent.resolve()
            path = dir / "output.log"
        else:
            path = Path(value)
            dir = path.parent.resolve()
            if path.is_dir():
                raise LogFileIsADirectory(path=path)
            if not dir.is_dir():
                raise LogPathDoesNotExist(path=dir)
            if not access(dir, X_OK):
                raise LogPathInsufficientPermissions(path=dir)

        self._output_file = path

        if path.is_file():
            self._clear_file()

    @property
    def level(self):
        return self._level

    @level.setter
    def level(self, value):
        level = value.upper()
        if level not in self._LEVELS:
            raise LogLevelDoesNotExist(level)
        self._level = level

    def _clear_file(self):
        with open(self._output_file, "w") as f:
            pass

    def _write(self, content):
        if not self._enabled:
            return
        time = Style.DIM + datetime.now().strftime("%H:%M:%S.%f")[:-3]
        dash = Style.BRIGHT + " - "
        with open(self._output_file, "a") as f:
            f.write(f"{time}{dash}{Style.NORMAL}{content}{Style.RESET_ALL}\n")

    def _is_valid_level(self, level):
        return self._LEVELS[self._level] <= self._LEVELS[level]

    def error(self, message):
        self._write(content=Fore.RED + message)

    def warn(self, message):
        if not self._is_valid_level("WARNING"):
            return
        self._write(content=Fore.YELLOW + message)

    def info(self, message):
        if not self._is_valid_level("INFO"):
            return
        self._write(content=Fore.BLUE + message)

    def debug(self, message):
        if not self._is_valid_level("DEBUG"):
            return
        self._write(content=Fore.WHITE + message)

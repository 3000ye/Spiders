import attrs
import logging
import colorlog
from typing import Optional
from datetime import datetime
from attr.validators import instance_of, min_len, optional


@attrs.define(kw_only=True, eq=False)
class Logger:
    """
    一个自定义的日志类，提供带有彩色输出的日志功能

    Attributes:
        name:       日志器的名称
        level:      日志器的级别
        file:       保存日志的文件路径默认为 None
        _logger:    底层的日志器对象

    Methods:
        debug:      记录一个调试级别的消息
        info:       记录一个信息级别的消息
        warning:    记录一个警告级别的消息
        error:      记录一个错误级别的消息
        critical:   记录一个严重级别的消息
    """

    name: str = attrs.field(validator=[instance_of(str), min_len(1)])
    level: str = attrs.field(default="DEBUG")
    file: Optional[str] = attrs.field(validator=optional(instance_of(str)), default=None)
    _logger = attrs.field(init=False, repr=False)

    def __attrs_post_init__(self) -> None:
        """
        初始化日志对象并设置日志配置
        """
        self._logger = logging.getLogger(self.name)
        for handler in self._logger.handlers[:]:
            self._logger.removeHandler(handler)
        formatter = colorlog.ColoredFormatter(
            "%(cyan)s[%(asctime)s.%(msecs)03d]%(reset)s | %(blue)s%(name)s%(reset)s | %(log_color)s%(levelname)s%(reset)s | %(log_color)s%(message)s",
            datefmt='%Y-%m-%d %H:%M:%S',
            log_colors={
                "DEBUG": "bold_cyan",
                "INFO": "bold_green",
                "WARNING": "bold_yellow",
                "ERROR": "bold_red",
                "CRITICAL": "bold_red,bg_white",
            }
        )

        # 设置日志输出到控制台
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        self._logger.addHandler(stream_handler)

        # 设置日志输出到ES
        # eshandler = EsLogHandler(app=self.name)
        # eshandler.setFormatter(formatter)
        # self._logger.addHandler(eshandler)

        # 设置日志输出到文件
        if self.file:
            today = datetime.today().strftime("%Y%m%d")
            self.file = self.file if today in self.file else self.file.replace(".log", f"_{today}.log")
            file_handler = logging.FileHandler(self.file, encoding="utf-8")
            file_handler.setFormatter(formatter)
            self._logger.addHandler(file_handler)

        levels = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR,
            "CRITICAL": logging.CRITICAL
        }
        self._logger.setLevel(levels.get(self.level, logging.DEBUG))

    def debug(self, msg: str) -> None:
        """
        记录一个调试级别的消息

        Args:
            msg (str): The message to be logged.
        """
        self._logger.debug(msg)

    def info(self, msg: str) -> None:
        """
        记录一个信息级别的消息

        Args:
            msg (str): The message to be logged.
        """
        self._logger.info(msg)

    def warning(self, msg: str) -> None:
        """
        记录一个警告级别的消息

        Args:
            msg (str): The message to be logged.
        """
        self._logger.warning(msg)

    def error(self, msg: str) -> None:
        """
        记录一个错误级别的消息

        Args:
            msg (str): The message to be logged.
        """
        self._logger.error(msg)

    def critical(self, msg: str) -> None:
        """
        记录一个严重级别的消息

        Args:
            msg (str): The message to be logged.
        """
        self._logger.critical(msg)

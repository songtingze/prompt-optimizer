import os
import sys
from contextvars import ContextVar
from pathlib import Path
from uuid import uuid4

from loguru import logger

_trace_id: ContextVar[str] = ContextVar('x_trace_id', default='')


class TraceID:
    """全链路追踪ID管理工具类
    提供设置和获取当前上下文追踪ID的静态方法
    """

    @staticmethod
    def set(trace_id: str = "") -> ContextVar[str]:
        """设置当前上下文的追踪ID

        Args:
            trace_id: 指定的追踪ID，为空则自动生成

        Returns:
            ContextVar[str]: 包含追踪ID的上下文变量
        """
        if not trace_id:
            trace_id = uuid4().hex
        _trace_id.set(trace_id)
        return _trace_id

    @staticmethod
    def get() -> str:
        """获取当前上下文的追踪ID

        Returns:
            str: 当前追踪ID，无则返回空字符串
        """
        return _trace_id.get("")


class AppLogger:
    """应用日志记录类
    集成控制台和文件输出，自动添加追踪信息
    """

    def __init__(self, app_name: str = "prompt_optimizer", level: str = 'INFO'):
        """初始化日志记录器"""
        self.log_path = Path(os.getcwd()) / 'logs' / app_name
        self.log_path.mkdir(parents=True, exist_ok=True)

        # 移除默认日志处理器
        logger.remove()

        # 添加控制台日志处理器
        logger.add(
            sink=sys.stdout,
            level=level.upper(),
            format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
                   "<level>{level}</level> | "
                   "<cyan>{trace_msg}</cyan> | "
                   "<blue>{file_path}</blue>:<yellow>{function}</yellow>:<red>{line}</red> | "
                   "<white>{message}</white>",
            filter=self._logger_filter,
            colorize=True,
            backtrace=True
        )

        # 添加文件日志处理器
        logger.add(
            sink=self.log_path / f"{app_name}.log",
            rotation="10 MB",
            level=level.upper(),
            encoding="utf-8",
            enqueue=True,
            compression='tar.gz',
            backtrace=True,
            filter=self._logger_filter,
            format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level} | {trace_msg} | "
                   "{file_path}:{function}:{line} | {message}"
        )
        self.log = logger

    def _logger_filter(self, record: dict):
        """日志过滤器，为每条日志添加追踪信息"""
        record['trace_msg'] = _trace_id.get()
        try:
            file_path = str(record['file']) if not hasattr(record['file'], 'path') else str(
                record['file'].path).replace(os.getcwd(), '')[1:]
            if len(file_path) > 30:
                file_path = f"...{file_path[-30:]}"
            record['file_path'] = file_path
        except Exception as e:
            record['file_path'] = f"error getting file path: {e}"

        return record

    # 以下方法代理原始日志方法，添加depth=1以确保正确的调用位置信息
    def trace(self, *args, **kwargs):
        return self.log.opt(depth=1).trace(*args, **kwargs)

    def debug(self, *args, **kwargs):
        return self.log.opt(depth=1).debug(*args, **kwargs)

    def info(self, *args, **kwargs):
        return self.log.opt(depth=1).info(*args, **kwargs)

    def warning(self, *args, **kwargs):
        return self.log.opt(depth=1).warning(*args, **kwargs)

    def error(self, *args, **kwargs):
        return self.log.opt(depth=1).error(*args, **kwargs)

    def critical(self, *args, **kwargs):
        return self.log.opt(depth=1).critical(*args, **kwargs)

    def patch(self, *args, **kwargs):
        return self.log.patch(*args, **kwargs)


# 全局日志实例
logger = AppLogger()

import logging
import sys
import os

LOG_FILE = "job_log.log"

# 레벨 구간별로 출력할 핸들러를 분리하기 위해 Filter를 만든다.
class InfoFilter(logging.Filter):
    """ERROR 미만인 레벨만 통과(<= WARNING, INFO, DEBUG)"""
    def filter(self, record: logging.LogRecord) -> bool:
        return record.levelno < logging.ERROR

class ErrorFilter(logging.Filter):
    """ERROR 이상인 레벨만 통과"""
    def filter(self, record: logging.LogRecord) -> bool:
        return record.levelno >= logging.ERROR


def get_logger(name="JobLogger"):
    """
    부모/자식 프로세스가 모두 공통으로 import해서 사용하는 로거.
    INFO 이하는 stdout, ERROR 이상은 stderr, 그리고 파일에도 모든 레벨 기록.
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)  # 필요하다면 INFO/DEBUG 등으로 조정
    
    # 이미 핸들러가 붙어 있으면 다시 붙이지 않도록 처리
    if logger.handlers:
        return logger

    # propagate = False를 주면, root logger로 로그가 전파되지 않으므로 중복출력 방지
    logger.propagate = False

    #
    # 1) stdout용 핸들러 (INFO 이하)
    #
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(logging.DEBUG)  # 하한은 DEBUG(=최소 레벨)
    # filter를 달아 ERROR 미만만 들어오도록
    stdout_handler.addFilter(InfoFilter())
    fmt = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    stdout_handler.setFormatter(fmt)
    logger.addHandler(stdout_handler)

    #
    # 2) stderr용 핸들러 (ERROR 이상)
    #
    stderr_handler = logging.StreamHandler(sys.stderr)
    stderr_handler.setLevel(logging.ERROR)
    # filter를 달아 ERROR 이상만 들어오도록
    stderr_handler.addFilter(ErrorFilter())
    stderr_handler.setFormatter(fmt)
    logger.addHandler(stderr_handler)

    #
    # 3) 파일 핸들러 (모든 레벨)
    #
    file_handler = logging.FileHandler(LOG_FILE, mode="a", encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(fmt)
    logger.addHandler(file_handler)

    return logger

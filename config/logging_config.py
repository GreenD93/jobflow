import logging

def get_logger():
    # 중앙 로거 가져오기
    logger = logging.getLogger("JobLogger")
    logger.setLevel(logging.INFO)  # 기본 로깅 레벨 설정

    # 이미 핸들러가 추가된 경우 중복 추가 방지
    if not logger.handlers:
        # 콘솔 핸들러 설정
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)  # 콘솔 출력 레벨
        console_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

        # 파일 핸들러 설정
        file_handler = logging.FileHandler("job_log.log")
        file_handler.setLevel(logging.INFO)  # 파일 출력 레벨
        file_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    return logger
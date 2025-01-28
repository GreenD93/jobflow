import logging

# 중앙 로깅 설정
logging.basicConfig(
    filename="job_log.log",
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

# 로거 인스턴스를 반환하는 함수
def get_logger(name="JobLogger"):
    return logging.getLogger(name)
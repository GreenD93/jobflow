import subprocess, threading

from config.logging_config import get_logger
logger = get_logger()

class Job:
    def __init__(self, 
                 name="",
                 description="",
                 script="",
                 params={}):
        """
        Job 클래스 초기화
        :param name: Job 이름
        :param script: 실행할 Python 파일 경로
        """
        
        self.name = name
        self.description = description
        self.script = script
        self.params = params

    def stream_output(self, pipe, log_func):
        """
        Subprocess 출력 스트림을 읽어서 로깅
        :param pipe: Subprocess의 stdout/stderr 스트림
        :param log_func: 로깅 함수 (logger.info 또는 logger.error)
        """
        for line in iter(pipe.readline, ""):
            log_func(f"{self.name}: {line.strip()}")

    def run(self):

        """Job 실행"""
        logger.info(f"Starting job: {self.name} - {self.description}")

        try:
            # Subprocess로 Python 파일 실행
            process = subprocess.Popen(
                ["python", self.script] + [f"--{k}={v}" for k, v in self.params.items()],
                stdout=subprocess.PIPE,  # 표준 출력 캡처
                stderr=subprocess.PIPE,  # 표준 에러 캡처
                text=True,
            )

            # 출력과 에러를 비동기로 로깅
            threading.Thread(target=self.stream_output, args=(process.stdout, logger.info), daemon=True).start()
            threading.Thread(target=self.stream_output, args=(process.stderr, logger.error), daemon=True).start()

            # 프로세스 종료 대기
            return_code = process.wait()

            if return_code == 0:
                logger.info(f"Job {self.name} completed successfully!")
            else:
                logger.error(f"Job {self.name} failed with return code: {return_code}")

        except Exception as e:
            logger.error(f"Error running job {self.name}: {e}")
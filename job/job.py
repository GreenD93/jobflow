# job.py

import subprocess
import threading
import time

from config.logging_config import get_logger
logger = get_logger()

class Job:
    def __init__(
        self,
        name="",
        description="",
        script="",
        params=None,
        dependencies=None,
        retries=1,
        retry_delay=0
    ):
        """
        Job 클래스 초기화
        :param name: Job 이름
        :param description: Job 설명
        :param script: 실행할 Python 파일 경로
        :param params: 실행에 필요한 파라미터 (dict)
        :param dependencies: 이 Job이 의존하는 Job들의 이름(list)
        :param retries: 실패 시 재시도 횟수
        :param retry_delay: 재시도 간격(초)
        """
        self.name = name
        self.description = description
        self.script = script
        self.params = params if params else {}
        self.dependencies = dependencies if dependencies else []
        self.retries = retries
        self.retry_delay = retry_delay

        self.success = False
        self.failed = False

    def stream_output(self, pipe, log_func):
        for line in iter(pipe.readline, ""):
            log_func(f"{self.name}: {line.strip()}")

    def run_subprocess(self):
        process = subprocess.Popen(
            ["python", self.script] + [f"--{k}={v}" for k, v in self.params.items()],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        threading.Thread(target=self.stream_output, args=(process.stdout, logger.info), daemon=True).start()
        threading.Thread(target=self.stream_output, args=(process.stderr, logger.error), daemon=True).start()

        return_code = process.wait()
        return return_code

    def run(self):
        logger.info(f"Starting job: {self.name} - {self.description}")

        attempt = 0
        while attempt < self.retries:
            attempt += 1
            logger.info(f"Attempt {attempt}/{self.retries} for job {self.name}")

            try:
                return_code = self.run_subprocess()
                if return_code == 0:
                    logger.info(f"Job {self.name} completed successfully!")
                    self.success = True
                    return
                else:
                    logger.error(f"Job {self.name} failed with return code: {return_code}")
            except Exception as e:
                logger.error(f"Error running job {self.name}: {e}")

            if attempt < self.retries:
                logger.info(f"Retrying job {self.name} after {self.retry_delay} seconds...")
                time.sleep(self.retry_delay)

        logger.error(f"Job {self.name} failed after {self.retries} attempts.")
        self.failed = True

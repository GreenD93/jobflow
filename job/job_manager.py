# job_manager.py

import yaml
import threading
import time
import sys

from config.logging_config import get_logger
logger = get_logger()

class JobManager:
    def __init__(self, config_file):
        self.config = self.load_config(config_file)

        self.workflow_name = self.config["workflow"]["name"]
        self.job_definitions = self.config["workflow"]["jobs"]

        # { job_name: Job 객체 }
        self.jobs = {}

        # { job_name: set(의존 job_name) }
        self.remaining_dependencies = {}

    def __enter__(self):
        logger.info(f"Entering job group: {self.workflow_name}")
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        logger.info(f"Exiting job group: {self.workflow_name}")
        if exc_type:
            logger.info(f"An exception occurred: {exc_value}")
        else:
            logger.info(f"Running all jobs in {self.workflow_name}...")

            # 기존 코드: for job in self.jobs.values(): job.run()
            # 병렬 및 의존성 관리를 위해 run_all_jobs() 호출
            self.run_all_jobs()

            logger.info(f"All jobs in {self.workflow_name} completed successfully!")

    def load_config(self, config_file):
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)
        return config

    def add_job(self, job):
        """
        사용자가 생성한 Job 인스턴스를 JobManager에 등록.
        """
        definition = self.job_definitions.get(job.name, {})

        # params 병합
        config_params = definition.get("params", {})
        merged_params = dict(job.params)
        for k, v in config_params.items():
            if k not in merged_params:
                merged_params[k] = v
        job.params = merged_params

        # dependencies: Job에 지정된게 없으면 config의 것을 사용
        if not job.dependencies:
            job.dependencies = definition.get("dependencies", [])

        # retries: Job에 지정된 값이 기본(1)이고, config에 값이 있으면 사용
        if job.retries == 1 and "retries" in definition:
            job.retries = definition["retries"]

        # retry_delay: Job에 지정된 값이 0이고, config에 값이 있으면 사용
        if job.retry_delay == 0 and "retry_delay" in definition:
            job.retry_delay = definition["retry_delay"]

        self.jobs[job.name] = job
        logger.info(
            f"Added job: {job.name} "
            f"(dependencies={job.dependencies}, retries={job.retries}, retry_delay={job.retry_delay})"
        )

    def run_all_jobs(self):
        """
        모든 Job을 의존성 순서에 맞춰 병렬 실행한다.
        """
        # remaining_dependencies 초기화
        for job_name, job in self.jobs.items():
            self.remaining_dependencies[job_name] = set(job.dependencies)

        completed_jobs = set()
        failed_jobs = set()
        running_jobs = set()

        workflow_failed = False
        
        while True:
            # 의존성이 모두 충족된 Job들 중 아직 실행 안 한 것만 골라서 실행
            ready_jobs = [
                name for name, deps in self.remaining_dependencies.items()
                if len(deps) == 0
                and name not in running_jobs
                and name not in completed_jobs
                and name not in failed_jobs
            ]

            threads = []
            for job_name in ready_jobs:
                job = self.jobs[job_name]
                thread = threading.Thread(target=self._run_job_wrapper, args=(job,))
                thread.start()
                threads.append(thread)
                running_jobs.add(job_name)

            if not ready_jobs:
                # 더 이상 실행할 Job이 없으면, 종료 조건 체크
                if len(completed_jobs) + len(failed_jobs) == len(self.jobs):
                    break
                time.sleep(1)  # 잠시 대기 후 다시 확인

            # 병렬 실행된 Job들이 끝날 때까지 대기
            for t in threads:
                t.join()

            # Job 실행 결과를 보고 실패가 있으면 즉시 종료
            for job_name in ready_jobs:
                job = self.jobs[job_name]
                if job.success:
                    completed_jobs.add(job_name)
                    running_jobs.remove(job_name)
                    # 성공한 Job을 의존하는 Job들의 deps에서 제거
                    for other_job, deps in self.remaining_dependencies.items():
                        deps.discard(job_name)
                elif job.failed:
                    failed_jobs.add(job_name)
                    running_jobs.remove(job_name)
                    logger.error(f"Job {job_name} failed. Stopping the entire workflow.")
                    workflow_failed = True
                    break

            if workflow_failed:
                break

        if workflow_failed:
            # 프로세스를 종료(Exit Code=1)
            logger.error("Workflow failed due to a job failure. Exiting process.")
            sys.exit(1)

        else:
            logger.info("All jobs in the workflow have been processed.")
            logger.info(f"Completed jobs: {completed_jobs}")
            logger.info(f"Failed jobs: {failed_jobs}")

    def _run_job_wrapper(self, job):
        job.run()

# main.py
import os

PYTHONPATH = os.path.dirname(os.path.abspath(__file__))
os.environ['PYTHONPATH'] = PYTHONPATH

from job.job import Job
from job.job_manager import JobManager

from config.logging_config import get_logger
logger = get_logger()

config_path = "config/config.yaml"

# Job 인스턴스를 생성하면서 dependencies, retries, retry_delay를 직접 넣을 수 있음
# (여기서는 예시로 dataset_etl_task만 코드로 재시도 횟수를 3회로 입력)
job1 = Job(
    name="dataset_etl_task",
    description="dataset_etl_task",
    script="src/dataset_etl.py",
)

# train_task는 config.yaml에 의존성이 없으므로, 여기서 직접 빈 리스트로 설정해도 됨
job2 = Job(
    name="train_task",
    description="train_task",
    script="src/train.py"
)

job3 = Job(
    name="inference_task",
    description="inference_task",
    script="src/inference.py",
    dependencies=["dataset_etl_task", "train_task"],  # 코드에서 직접 작성도 가능
    retries=1
)

with JobManager(config_path) as group:
    group.add_job(job1)
    group.add_job(job2)
    group.add_job(job3)

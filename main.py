from job.job import Job
from job.job_manager import JobManager

from config.logging_config import get_logger
logger = get_logger()

config_path = "config/config.yaml"

job1 = Job(name="dataset_etl_task",
          description="dataset_etl_task",
          script="src/dataset_etl.py"
         )

job2 = Job(name="train_task",
          description="train_task",
          script="src/train.py"
         )

job3 = Job(name="inference_task",
          description="inference_task",
          script="src/inference.py"
         )

with JobManager(config_path) as group:
    group.add_job(job1)
    group.add_job(job2)
    group.add_job(job3)
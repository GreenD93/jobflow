import yaml

from config.logging_config import get_logger
logger = get_logger()

class JobManager:

    def __init__(self,
                 config_file):

        self.jobs = []
        self.config = self.load_config(config_file)

        self.job_def = self.config.get("workflow")["jobs"]
        self.name = self.config.get("workflow")["name"]

    def __enter__(self):
        logger.info(f"Entering job group: {self.name}")
        return self

    def __exit__(self, exc_type, exc_value, traceback):

        logger.info(f"Exiting job group: {self.name}")

        if exc_type:
            logger.info(f"An exception occurred: {exc_value}")
        else:
            logger.info(f"Running all jobs in {self.name}...")
            for job in self.jobs:
                job.run()
            logger.info(f"All jobs in {self.name} completed successfully!")

    def load_config(self, config_file):

        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)

        return config

    def add_job(self, job):

        job_def = self.job_def[job.name]
        params = job_def.get("params", "")

        job.params = params

        self.jobs.append(job)

        logger.info(f"Added job: {job.name}")
        logger.info(f"{job_def}")
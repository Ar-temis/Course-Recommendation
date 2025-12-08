from pathlib import Path
from crec.ingestion import courses, major_req_dict, schedule
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

log = logging.getLogger(__file__)
log.setLevel(logging.INFO)


if __name__ == "__main__":
    logging.info("Setup process starting...")
    db_dir = Path(__file__).parent.parent.joinpath("dbs/")
    data_dir = Path(__file__).parent.parent.joinpath("data/")

    db_dir.mkdir(exist_ok=True)

    logging.info("Setting up courses...")
    courses.pipeline(data_dir)
    logging.info("Finished setting up courses")
    logging.info("Setting up majors...")
    major_req_dict.pipeline(data_dir)
    logging.info("Finished setting up majors")
    logging.info("Setting up schedules...")
    schedule.pipeline(data_dir)
    logging.info("Finished setting up schedules")

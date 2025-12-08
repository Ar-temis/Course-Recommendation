import sqlite3

from crec.config import config
from typing import Optional
import dspy
from pydantic import BaseModel
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

log = logging.getLogger(__file__)
log.setLevel(logging.INFO)


class Schedule(BaseModel):
    id: int
    session: str
    subject: str
    catalog_num: str
    section: str
    course_name: str
    start_time: str
    end_time: str
    scheduled_days: str
    credits: float


SUBJECTS = [
    "DKU",
    "GERMAN",
    "INDSTU",
    "JAPANESE",
    "KOREAN",
    "MUSIC",
    "SPANISH",
    "ARHU",
    "ARTS",
    "BEHAVSCI",
    "BIOL",
    "CHEM",
    "CHINESE",
    "COMPDSGN",
    "COMPSCI",
    "CULANTH",
    "CULMOVE",
    "CULSOC",
    "EAP",
    "ECON",
    "ENVIR",
    "ETHLDR",
    "GCHINA",
    "GCULS",
    "GLHLTH",
    "HIST",
    "HUM",
    "INFOSCI",
    "INSTGOV",
    "LIT",
    "MATH",
    "MATSCI",
    "MEDIA",
    "MEDIART",
    "NEUROSCI",
    "PHIL",
    "PHYS",
    "PHYSEDU",
    "POLECON",
    "POLSCI",
    "PPE",
    "PSYCH",
    "PUBPOL",
    "SOCIOL",
    "SOSC",
    "STATS",
    "USTUD",
    "WOC",
    "RELIG",
    "MINITERM",
]


class subject_rewriter_signature(dspy.Signature):
    """
    Return the closest subject out of the possible subjects.
    Return None if no subject is close.
    """

    possible_subjects: list[str] = dspy.InputField()
    candidate: str = dspy.InputField(
        desc="A subject query that might have a typo or written wrongly."
    )
    valid_subject: str = dspy.OutputField()


def __retrieve_results(sql_query: str, inputs: tuple[str]) -> list[Schedule]:
    with sqlite3.connect(
        config.schedule_db,
    ) as conn:
        cursor = conn.cursor()
        cursor.row_factory = sqlite3.Row

        temp = conn.execute(sql_query, inputs).fetchall()
    results = []

    for t in temp:
        # Source - https://stackoverflow.com/a
        # Posted by ant1fact
        # Retrieved 2025-12-06, License - CC BY-SA 4.0
        s = Schedule(**{k: v for k, v in zip(Schedule.model_fields.keys(), t)})
        results.append(s)

    return results


def schedule_retriever(
    # TODO: For now let's focus on one session at a time
    # session: Optional[str] = None,
    subject_code: str,
    # TODO: Some numbers such as Chinese 101A has letters in them
    catalog_num: Optional[int] | Optional[list[int]] = None,
) -> str:
    """
    Retrieve course schedules from the schedule database.

    Queries the database using subject code and optional catalog number.

    Args:
        subject_code: Subject code (e.g., 'COMPSCI', 'MATH').
        catalog_num: If provided, filters results to a specific course.
            If None, retrieves all courses for the subject.

    Returns:
        Query results containing course schedule information including session,
        catalog number, section, course name, time slots, scheduled days, and credits.
    """
    # TODO: Put in available subjects in the docstring

    logger.info(f"Subject: {subject_code}, Codes: {catalog_num}")

    sql_query = ""
    inputs = None

    if not (subject_code is None or subject_code in SUBJECTS):
        logger.info("Predicting subject")
        subject_rewriter = dspy.Predict(subject_rewriter_signature)
        result = subject_rewriter(possible_subjects=SUBJECTS, candidate=subject_code)
        logger.info(f"Predicted Subject: {result}")
        if result == "None":
            msg = f"{subject_code} does not exist in the schedule db."
            return LookupError(msg)

    if subject_code and catalog_num:
        if isinstance(catalog_num, int):
            catalog_num = [catalog_num]

        placeholders = ",".join(["?"] * len(catalog_num))
        sql_query = f"""
            SELECT id, session, subject, catalog_num, section,
            course_name, start_time, end_time, scheduled_days, credits
            FROM spring_schedule
            WHERE subject = ?
            AND catalog_num IN ({placeholders});
        """
        inputs = (subject_code, *catalog_num)

    elif subject_code and (catalog_num is None):
        sql_query = """
            SELECT id, session, subject, catalog_num, section,
            course_name, start_time, end_time, scheduled_days, credits
            FROM spring_schedule
            WHERE subject = ?;
        """
        inputs = (subject_code,)
    else:
        # Even though subject is required above
        # This is for safety i guess
        msg = "subject argument is missing"
        return ValueError(msg)

    results = __retrieve_results(sql_query, inputs)
    logger.info(f"Retrieved results: {results}")
    return results

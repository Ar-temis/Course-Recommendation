import pytest
from unittest.mock import patch, MagicMock
from crec.tools.schedule_ret import schedule_retriever, Schedule

MOCK_SCHEDULE = [
    Schedule(
        id=1,
        session="Spring 2026",
        subject="COMPSCI",
        catalog_num="101",
        section="01",
        course_name="Intro to CS",
        start_time="09:00",
        end_time="10:20",
        scheduled_days="MWF",
        credits=3.0,
    )
]


class TestScheduleRetriever:
    @patch("crec.tools.schedule_ret.__retrieve_results")
    def test_correct_subject(self, mock_retrieve):
        mock_retrieve.return_value = MOCK_SCHEDULE
        result = schedule_retriever(subject_code="COMPSCI")

        assert result == MOCK_SCHEDULE
        mock_retrieve.assert_called_once()
        sql_query, inputs = mock_retrieve.call_args[0]
        assert "WHERE subject = ?" in sql_query
        assert inputs == ("COMPSCI",)

    @patch("crec.tools.schedule_ret.__retrieve_results")
    def test_correct_subject_and_correct_course_number(self, mock_retrieve):
        mock_retrieve.return_value = MOCK_SCHEDULE
        result = schedule_retriever(subject_code="COMPSCI", catalog_num=101)

        assert result == MOCK_SCHEDULE
        mock_retrieve.assert_called_once()
        sql_query, inputs = mock_retrieve.call_args[0]
        assert "WHERE subject = ?" in sql_query
        assert "catalog_num IN (" in sql_query
        assert inputs == ("COMPSCI", 101)

    @patch("crec.tools.schedule_ret.dspy.Predict")
    @patch("crec.tools.schedule_ret.__retrieve_results")
    def test_incorrect_subject(self, mock_retrieve, mock_predict_cls):
        mock_retrieve.return_value = MOCK_SCHEDULE
        mock_predict_instance = MagicMock()
        mock_predict_instance.return_value = "COMPSCI"
        mock_predict_cls.return_value = mock_predict_instance

        result = schedule_retriever(subject_code="COMPSCI_X")

        mock_predict_cls.assert_called_once()
        mock_retrieve.assert_called_once()
        sql_query, inputs = mock_retrieve.call_args[0]
        assert inputs == ("COMPSCI",)
        assert result == MOCK_SCHEDULE

    @patch("crec.tools.schedule_ret.dspy.Predict")
    @patch("crec.tools.schedule_ret.__retrieve_results")
    def test_incorrect_subject_and_correct_course_number(self, mock_retrieve, mock_predict_cls):
        mock_retrieve.return_value = MOCK_SCHEDULE
        mock_predict_instance = MagicMock()
        mock_predict_instance.return_value = "COMPSCI"
        mock_predict_cls.return_value = mock_predict_instance

        result = schedule_retriever(subject_code="COMPSCI_X", catalog_num=101)

        mock_predict_cls.assert_called_once()
        mock_retrieve.assert_called_once()
        sql_query, inputs = mock_retrieve.call_args[0]
        assert "catalog_num IN (" in sql_query
        assert inputs == ("COMPSCI", 101)
        assert result == MOCK_SCHEDULE

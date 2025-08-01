import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
import pytest
from clickup_service import ClickUpService


def test_format_task_row_pipe():
    service = ClickUpService()
    task = {
        'name': 'Dirt Vision | Subject',
        'url': 'http://example.com',
        'priority': {'priority': 'high'},
        'status': {'status': 'Open'},
        'custom_fields': [{'name': 'Work email address?', 'value': 'user@example.com'}],
        'board_name': 'Board1'
    }
    row = service.format_task_row(task, True)
    assert row == ['Dirt Vision', 'http://example.com', 'Subject', 'high', 'Open', 'user@example.com', 'Board1']

def test_format_task_row_no_pipe():
    service = ClickUpService()
    task = {
        'name': 'NoPipeTask',
        'url': 'http://example.com',
        'priority': {},
        'status': {},
        'custom_fields': [],
        'board_name': 'Board1'
    }
    row = service.format_task_row(task, False)
    assert row == ['', 'http://example.com', 'NoPipeTask', 'normal', 'Unknown', 'Not Available', 'Board1']

def test_calculate_data_ranges():
    service = ClickUpService()
    r1, rlabel, r2 = service.calculate_data_ranges(2, [[1],[2]], [[3]])
    assert r1 == 'A2:G3'
    assert rlabel == 'A4:G4'
    assert r2 == 'A5:G5'

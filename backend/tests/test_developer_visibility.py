import unittest

from utils.visibility import get_developer_visible_request_ids


class DummyDevelopmentRow:
    def __init__(self, request_id, assigned_to):
        self.RequestID = request_id
        self.AssignedTo = assigned_to


class DeveloperVisibilityTests(unittest.TestCase):
    def test_shows_unassigned_and_self_assigned_requests(self):
        rows = [
            DummyDevelopmentRow(101, None),
            DummyDevelopmentRow(102, 7),
            DummyDevelopmentRow(103, 9),
        ]

        visible = get_developer_visible_request_ids(rows, 7)

        self.assertEqual(visible, [101, 102])


if __name__ == "__main__":
    unittest.main()

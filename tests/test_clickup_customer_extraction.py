import unittest
from src.clickup_service import ClickUpService

class TestClickUpServiceCustomerExtraction(unittest.TestCase):
    def setUp(self):
        self.service = ClickUpService()

    def test_extract_customer_name(self):
        cases = [
            ('"Dirt Vision" | Streaming issue', 'Dirt Vision'),
            ('"Gotham/Yes" | Login bug', 'Gotham/Yes'),
            ('"Marquee" | Feature request', 'Marquee'),
            ('"Wurl" | API error', 'Wurl'),
            ('"Yahoo" | UI feedback', 'Yahoo'),
            ('No quotes or pipe', None),
            ('"Customer Only"', None),
            ('"Another Customer" |', 'Another Customer'),
        ]
        for task_name, expected in cases:
            with self.subTest(task_name=task_name):
                self.assertEqual(self.service.extract_customer_name(task_name), expected)

    def test_get_customer_tab_name(self):
        self.assertEqual(self.service.get_customer_tab_name('Dirt Vision'), 'Dirt Vision')
        self.assertEqual(self.service.get_customer_tab_name(''), 'Uncategorized')
        self.assertEqual(self.service.get_customer_tab_name(None), 'Uncategorized')
        long_name = 'A' * 120
        self.assertEqual(len(self.service.get_customer_tab_name(long_name)), 30)

if __name__ == "__main__":
    unittest.main()

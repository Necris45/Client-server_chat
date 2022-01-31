import sys
import os
import unittest
# Для импорта с директории, находящейся уровнем выше.
sys.path.append(os.path.join(os.getcwd(), '..'))
from common.variables import RESPONSE, ERROR, USER, ACCOUNT_NAME, TIME, ACTION, PRESENCE
from client import create_presence, process_ans


class TestClass(unittest.TestCase):

    def test_def_presence(self):
        """Тест коректного запроса"""
        test = create_presence()
        test[TIME] = 2.3  # время необходимо приравнять принудительно, иначе тест никогда не будет пройден
        self.assertEqual(test, {ACTION: PRESENCE, TIME: 2.3, USER: {ACCOUNT_NAME: 'Guest'}})
        print("test_def_presence complete")

    def test_200_answer(self):
        """Тест корректного разбора ответа 200"""
        self.assertEqual(process_ans({RESPONSE: 200}), '200 : OK')
        print("test_200_answer complete")

    def test_400_answer(self):
        """Тест корректного разбора 400"""
        self.assertEqual(process_ans({RESPONSE: 400, ERROR: 'Bad Request'}), '400 : Bad Request')
        print("test_400_answer complete")

    def test_no_response(self):
        """Тест исключения без поля RESPONSE"""
        self.assertRaises(ValueError, process_ans, {ERROR: 'Bad Request'})
        print("test_no_response complete")


if __name__ == '__main__':
    unittest.main()

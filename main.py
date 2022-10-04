from test_cases import AirBnbTests
import unittest


if __name__ == '__main__':
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(AirBnbTests)
    unittest.TextTestRunner().run(suite)

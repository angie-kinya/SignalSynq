import unittest
from detector import TrafficSignalController

class TestTrafficSignal(unittest.TestCase):
    def setUp(self):
        self.controller = TrafficSignalController()
        
    def test_signal_timing(self):
        # Test equal distribution
        counts = {"lane1": 10, "lane2": 10}
        times = self.controller.calculate_signal_timing(counts)
        self.assertEqual(times["lane1"], times["lane2"])
        
        # Test heavy traffic on one lane
        counts = {"lane1": 30, "lane2": 5}
        times = self.controller.calculate_signal_timing(counts)
        self.assertGreater(times["lane1"], times["lane2"])
        
    def test_route_recommendation(self):
        counts = {"main": 20, "alternative": 5}
        rec = self.controller.get_route_recommendation("main", counts)
        self.assertIn("alternative", rec)

if __name__ == '__main__':
    unittest.main()
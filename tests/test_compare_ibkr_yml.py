import unittest
import pandas as pd
from datetime import datetime
from pathlib import Path
from exchanges.compare_ibkr_yml import compare_sessions
import pytz


class TestCompareSessions(unittest.TestCase):
    def test_compare_sessions(self):
        symbol = "QQQ"
        tz = pytz.timezone("America/New_York")
        date_ = tz.localize(datetime.strptime("2000-01-05", "%Y-%m-%d"))
        ibkr_data = pd.DataFrame(
            {
                "Starttime": [
                    datetime.strptime("2000-01-05 09:30:00", "%Y-%m-%d %H:%M:%S")
                ],
                "Endtime": [
                    datetime.strptime("2000-01-05 16:00:00", "%Y-%m-%d %H:%M:%S")
                ],
                "Symbol": ["QQQ"],
            }
        )
        for col in ["Starttime", "Endtime"]:
            ibkr_data[col] = pd.to_datetime(ibkr_data[col]).apply(
                lambda x: tz.localize(x)
            )
        yml_file = Path(__file__).with_name("valid.yaml")
        result = compare_sessions(symbol, date_, ibkr_data, yml_file)
        self.assertIsNone(result, "Test failed: Expected None")


if __name__ == "__main__":
    unittest.main()

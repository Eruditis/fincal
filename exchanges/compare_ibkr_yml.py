"""
This module contains the function compare_sessions which compares 
trading sessions from IBKR data and a YAML file.
It also contains a main function which reads the IBKR data from a file, 
loops over symbols and dates, and calls the compare_sessions function for each.
Usage:
from exchanges.compare_ibkr_yml import compare_sessions

To run the main function
python fincal/exchanges/compare_ibkr_yml.py
"""
from exchanges.sessions import GetSessions
import pandas as pd
import pytz
from datetime import datetime
import logging
import sys
from pathlib import Path


def compare_sessions(symbol, date_, ibkr_data, yml_file, file_=None):
    """
    This function compares trading sessions from IBKR data and a YAML file.

    Parameters:
    symbol (str): The symbol for which to compare sessions.
    date_ (datetime): The date for which to compare sessions.
    ibkr_data (DataFrame): The DataFrame containing IBKR data.
    yml_file (str): The path to the YAML file containing session data.
    file_ (file, optional): An optional file to which to write the comparison results.

    Returns:
    dict: A dictionary containing the comparison results.
    """
    logging.info(f"running for symbol:{symbol}, date:{date_}")
    sessions = GetSessions(date_, yml_file)
    regular_session = None
    data_ = ibkr_data[
        (ibkr_data["Starttime"].dt.date == date_.date())
        & (ibkr_data["Symbol"] == symbol)
    ]
    for session in sessions:
        if session["session"] == "NYSE American Core Trading":
            regular_session = session
            tzinfo = pytz.timezone(regular_session["timezone"])
            session_start = tzinfo.localize(
                datetime.strptime(
                    f"{regular_session['date']} {regular_session['gte']['time']}",
                    "%Y-%m-%d %I:%M %p",
                )
            )
            session_end = tzinfo.localize(
                datetime.strptime(
                    f"{regular_session['date']} {regular_session['lt']['time']}",
                    "%Y-%m-%d %I:%M %p",
                )
            )
    if (not data_.empty) and regular_session:
        if (data_["Starttime"].iloc[0] == session_start) and (
            data_["Endtime"].iloc[0] == session_end
        ):
            return
        diff = {
            "symbol": symbol,
            "ibkr_session_start": data_["Starttime"].iloc[0],
            "ibkr_session_end": data_["Endtime"].iloc[0],
            "yml_session_start": session_start,
            "yml_session_end": session_end,
        }
    if data_.empty and (not regular_session):
        return
    if data_.empty:
        diff = {
            "symbol": symbol,
            "ibkr_session_start": "",
            "ibkr_session_end": "",
            "yml_session_start": session_start,
            "yml_session_end": session_end,
        }

    if not regular_session:
        diff = {
            "symbol": symbol,
            "ibkr_session_start": data_["Starttime"].iloc[0],
            "ibkr_session_end": data_["Endtime"].iloc[0],
            "yml_session_start": "",
            "yml_session_end": "",
        }
    if file_:
        file_.write(f"{','.join(map(str, list(diff.values())))}\n")
    return diff


def main():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler(sys.stdout)
    logger.addHandler(handler)
    ibkr_data = pd.read_csv("~/fincal/data/ibkr_sessions.txt")
    file_ = open(Path("~/fincal/data/compare_ibkr_yml.txt").expanduser(), "w")
    file_.write(
        "symbol,ibkr_session_start,ibkr_session_end,yml_session_start,yml_session_end\n"
    )
    tz = pytz.timezone("America/New_York")
    for col in ["Starttime", "Endtime"]:
        ibkr_data[col] = pd.to_datetime(ibkr_data[col]).apply(lambda x: tz.localize(x))
    for symbol, exchange_yml in [
        ("QQQ", "exchanges/xnas.yml"),
        ("KO", "exchanges/nyse.yml"),
    ]:
        for date_ in pd.date_range(
            start=pd.Timestamp("20000105"),
            end=pd.Timestamp("20231231"),
            tz="America/New_York",
        ):
            compare_sessions(symbol, date_, ibkr_data, exchange_yml, file_)
    file_.close()


if __name__ == "__main__":
    main()

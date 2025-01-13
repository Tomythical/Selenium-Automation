from datetime import datetime


def parse_server_clock(clock_text: str) -> datetime:
    return datetime.strptime(clock_text, "%I:%M:%S %p").time()

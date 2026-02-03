from datetime import datetime, timedelta
import pytz

TIMEZONE = "America/New_York"

def compute_lookback_window(now_et: datetime) -> tuple[datetime, datetime]:
    """
    Publishes at 7:00 AM ET. Lookback logic:
    - Tue–Fri: previous 24 hours
    - Mon: Fri 7:00 AM → Mon 7:00 AM
    - (If run on weekend, still use last 24 hours; but you said you won't publish weekends.)
    """
    if now_et.tzinfo is None:
        raise ValueError("now_et must be timezone-aware ET datetime")

    end = now_et
    weekday = now_et.weekday()  # Mon=0 ... Sun=6

    # If it's Monday, include weekend: go back 3 days (Fri -> Mon) relative to 7am cadence
    # If Monday(0), Saturday(5), or Sunday(6), extend lookback to capture Friday news
    if weekday in (0, 5, 6):
        start = end - timedelta(days=3)
    else:
        start = end - timedelta(hours=24)

    return start, end

def now_et(tz_name: str) -> datetime:
    tz = pytz.timezone(tz_name)
    return datetime.now(tz)

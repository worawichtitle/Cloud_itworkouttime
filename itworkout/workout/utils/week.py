from datetime import datetime, timedelta, date

def get_week_dates(reference_date=None):
    if reference_date is None:
        reference_date = datetime.today()

    start_of_week = reference_date - timedelta(days=reference_date.weekday())  # Monday
    week_dates = [(start_of_week + timedelta(days=i)) for i in range(7)]

    return week_dates  # [datetime, ..., datetime]

def format_week_dates(week_dates):
    return [date.strftime("%d-%m-%Y") for date in week_dates]  # ['02-10-2025', ..., '30-10-2025']

def get_duration_minutes(start, end):
        # delta = datetime.combine(date.today(), end) - datetime.combine(date.today(), start)
    delta = end - start
    return delta.total_seconds() / 60
import datetime


def get_week():
    date = datetime.date.today()
    week = date.isocalendar().week
    return week

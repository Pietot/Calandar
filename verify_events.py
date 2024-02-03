""" Create a calendar that sends a notification 1 week before,
    1 day before and on the day of an event.
"""


# By Piétôt
# Discord : Piétôt#1754 | Pietot
# Start : 25/06/2023 at 00h56 FR
# End : 26/06/2023 at 20h27 FR


# Importing usefull modules:
# json to load, save and create data
# os pour créer des fichier
# datetime to manipulate date


import json
import os

from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from win10toast import ToastNotifier


class MyCalendar():
    """ Create a calendar that sends a notification 1 week before,
        1 day before and on the day of an event.
    """

    def __init__(self) -> None:
        self.today_date = datetime.today().date()
        self.data_path = "dates.json"
        self.icon_path = "icon.ico"
        if not os.path.exists(self.data_path):
            with open(self.data_path, 'w', encoding='utf-8'):
                pass
        with open(self.data_path, 'r+', encoding='utf-8') as file_data:
            try:
                self.data = json.load(file_data)
            except json.JSONDecodeError:
                self.data: dict[str, list[dict[str, str | bool | None]]] = {
                    "event": []}
                json.dump(self.data, file_data)

    def add_new_event(self, day: int,
                      month: int | None = None,
                      year: int | None = None,
                      label: str | None = None,
                      cycle: bool = False) -> None:
        """ Add a new event to the json file

        Args:
            day (int): The event's day
            month (int | None, optional): The event's month.
                The current month if None. Defaults to None.
            year (int | None, optional): The event's year.
                The current year if None. Defaults to None.
            label (str | None, optional): The event's label. Defaults to None.
            cycle (bool, optional): If the event will be triggered each year.
                Defaults to False

        Raises:
            TimeoutError: If the given date is gone
        """
        event_day = self.verify_date(day, 'day')
        event_month = self.verify_date(month, 'month')
        event_year = self.verify_date(year, 'year')
        event_date = date(event_year, event_month, event_day)
        if event_date <= self.today_date:
            raise TimeoutError(f'{event_date} has passed')
        new_event = {
            "date": str(event_date),
            "label": label,
            "cycle": cycle
        }
        self.data['event'].append(new_event)
        # Sort all events by the date in ascending order
        self.data['event'] = sorted(self.data['event'],
                                    key=lambda x: datetime.strptime(str(x['date']),
                                                                    '%Y-%m-%d').date())
        with open(self.data_path, 'w', encoding='utf-8') as file_data:
            json.dump(self.data, file_data)

    def verify_date(self, value: None | int, data_type: str) -> int:
        """ Verify if a date of a day/month/year is correct

        Args:
            value (None | int): The number of a date
            data_type (str): If it's a day/month/year

        Raises:
            ValueError: If a month is not in the range [1,12]
            ValueError: If a years is passed
            ValueError: If the datatype is not as expected

        Returns:
            int: The value of de date
        """
        if data_type == 'day':
            assert value is not None, "What day you want ?"
            assert 1 <= value <= 31, "One month has at best 31 days"
            return value
        if data_type == 'month':
            if value is None:
                return self.today_date.month
            if not 1 <= value <= 12:
                raise ValueError('One year has 12 months')
            return value
        if data_type == 'year':
            if value is None:
                return self.today_date.year
            if value < self.today_date.year:
                raise ValueError(f'Year {value} has been exceeded')
            return value
        raise ValueError(f"Type \"{data_type}\" is not as expected")

    def verify_events(self) -> None:
        """ Verify the date of an event and throw a notification

        Returns:
            None
        """
        for index, event in enumerate(self.data['event']):
            # Convert to str to match with datetime.strptime
            event_date = datetime.strptime(
                str(event['date']), '%Y-%m-%d').date()
            remaining_day = (event_date - self.today_date).days
            print(event, remaining_day)
            if remaining_day < 0:
                if event['cycle']:
                    self.update_date_event(index, event_date)
                else:
                    self.delete_event(index)
            # Day of event has arrived
            if remaining_day == 0:
                self.throw_windows_notification(
                    str(event['label']), "aujourd'hui !")
            # 1 day remaining berfore the event
            elif remaining_day == 1:
                self.throw_windows_notification(
                    str(event['label']), "demain !")
            # 1 week remaining berfore the event
            elif remaining_day == 7:
                self.throw_windows_notification(
                    str(event['label']), "la semaine prochaine !")
            else:
                return None
        return None

    def update_date_event(self, index: int, event_date: date) -> None:
        """ Update the date of an event

        Args:
            index (int): The index of the event
            event_date (date): The date of the event
        """
        new_date = event_date + relativedelta(years=1)
        self.data['event'][index]['date'] = str(new_date)
        # Sort all events by the date in ascending order
        self.data['event'] = sorted(self.data['event'],
                                    key=lambda x: datetime.strptime(str(x['date']),
                                                                    '%Y-%m-%d').date())
        with open(self.data_path, 'w', encoding='utf-8') as file_data:
            json.dump(self.data, file_data)

    def throw_windows_notification(self, label: str, time: str) -> None:
        """ Throw a windows notifiaction

        Args:
            label (str): The message in the notification
        """
        toaster = ToastNotifier()
        toaster.show_toast(title="Event Reminder !",
                           msg=f'Message: {label}, {time}',
                           icon_path=self.icon_path,
                           duration=20)

    def delete_event(self, index: int) -> None:
        """ Deletes an event

        Args:
            index (int): The index of an event
        """
        if index < 0:
            return
        del self.data['event'][index]
        with open(self.data_path, 'w', encoding='utf-8') as file_data:
            json.dump(self.data, file_data)


if __name__ == '__main__':
    MyCalendar().verify_events()

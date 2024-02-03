"""Shows all events, adds or deletes an event to the json file"""


import json
import os

from datetime import datetime, date


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

    def delete_event(self, index: int) -> None:
        """ Deletes an event

        Args:
            index (int): The index of an event
        """
        if index < 0:
            raise IndexError("Index out of range")
        del self.data['event'][index]
        with open(self.data_path, 'w', encoding='utf-8') as file_data:
            json.dump(self.data, file_data)

    def show_events(self) -> None:
        """ Show all events
        """
        with open(self.data_path, 'r', encoding='utf-8') as file_data:
            data = json.load(file_data)
            if not data['event']:
                print("No events")
                return
            for event in data['event']:
                print(event)
                print('----------------------------------------')


if __name__ == "__main__":
    calendar = MyCalendar()

    while (user_response := input(
            'Show upcoming events, add one or delete one? (s/a/d)\n')) != '':
        if user_response == 's':
            calendar.show_events()
        elif user_response == 'a':
            user_day = int(input("What day?\n"))
            user_month = input("What month?\n")
            user_month = int(user_month) if user_month != "" else None
            user_year = input("What year?\n")
            user_year = int(user_year) if user_year != "" else None
            user_label = input("Insert a message: (optional)\n")
            user_label = user_label if user_label != "" else None
            user_cycle = input("Do you want to repeat the event every year? (y/n)\n")
            user_cycle = bool(user_cycle) if user_cycle == 'y' else False

            print(
                f"{user_day}/{user_month}/{user_year}\nMessage:{user_label}\nCycle: {user_cycle}")

            try:
                is_all_good = input("Is it good for you? (y/n)\n")
                is_all_good = bool(is_all_good) if is_all_good == 'y' else False
                if is_all_good:
                    calendar.add_new_event(
                        user_day, user_month, user_year, user_label, user_cycle)
                    print("Event added!")
                else:
                    print("Event not added")
            except TimeoutError:
                print("The date does not exist")
            except Exception as e:  # pylint: disable=broad-exception-caught
                print("Error:")
                print(e)
        elif user_response == 'd':
            calendar.show_events()
            try:
                user_index = int(
                    input("Which event do you want to delete? (Index starts at 0)\n"))
            except ValueError:
                print("Index must be a number")
            else:
                calendar.delete_event(user_index)

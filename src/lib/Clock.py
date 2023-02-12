from dataclasses import dataclass, field
from datetime import datetime, timedelta, time, date
from os import path
from json import JSONDecodeError

import json, csv

@dataclass
class Clock:
    _date: date | None
    _time_in: time | None
    _time_out: time | None
    _lunch_time_start: time | None
    _lunch_time_stop: time | None
    _is_clocked_in: bool
    _work_notes: str | None

    def __post_init__(self) -> None:
        self._total_hours: int | None = self.calculate_time() if self._time_out is not None and self._time_in is not None else None

    def __getitem__(self, item):
        pass

    @property
    def date(self) -> str | None:
        return str(self._date) if self._date else None
    
    @date.setter
    def date(self, new_value: datetime | None) -> None:
        self._date = new_value

    @property
    def time_in(self) -> str | None:
        return str(self._time_in) if self._time_in else None
    
    @time_in.setter
    def time_in(self, new_value: time | None) -> None:
        self._time_in = new_value

    @property
    def time_out(self) -> str | None:
        return str(self._time_out) if self._time_out else None
    
    @time_out.setter
    def time_out(self, new_value: time | None) -> None:
        self._time_out = new_value

    @property
    def lunch_time_start(self) -> str | None:
        return str(self._lunch_time_start) if self._lunch_time_start else None
    
    @lunch_time_start.setter
    def lunch_time_start(self, new_value: time | None) -> None:
        self._lunch_time_start = new_value

    @property
    def lunch_time_stop(self) -> str | None:
        return str(self._lunch_time_stop) if self._lunch_time_stop else None
    
    @lunch_time_stop.setter
    def lunch_time_stop(self, new_value: time | None) -> None:
        self._lunch_time_stop = new_value

    @property
    def is_clocked_in(self) -> bool:
        return self._is_clocked_in
    
    @is_clocked_in.setter
    def is_clocked_in(self, new_value: bool | None) -> None:
        self._is_clocked_in = new_value

    @property
    def total_hours(self) -> int | None:
        return self._total_hours if self._total_hours is not None else None
    
    @total_hours.setter
    def total_hours(self, new_value: int | None) -> None:
        self._total_hours = new_value
    
    @property
    def lunch_total_time(self) -> int | None:
        return self._lunch_total_time if self._lunch_total_time is not None else None

    @property
    def work_notes(self) -> str | None:
        return self._work_notes if self._work_notes else None
    
    @work_notes.setter
    def work_notes(self, new_value: str | None) -> None:
        self._work_notes = new_value

    # Save the current class state to clock.json
    def save(self):
        try:
            with open('clock.json', 'w') as clock_file:
                clock_file.write(json.dumps(self.to_dict(), indent=4))
        except IOError as err:
            print(f"{err}: Could not write to clock.json")

    # Return a dictionary representing the current object, and it's state.
    def to_dict(self) -> dict:
        return {
            "date": self.date,
            "time_in": self.time_in,
            "time_out": self.time_out,
            "lunch_time_start": self.lunch_time_start,
            "lunch_time_stop": self.lunch_time_stop,
            "is_clocked_in": self.is_clocked_in,
            "work_notes": self.work_notes,
            "total_hours": self.total_hours
        }
    
    # Calultate the time based on time_in and time_out while also subtracting the lunch
    def calculate_time(self) -> str:
        # Calculate time with no lunch
        if self._lunch_time_start is None or self._lunch_time_stop is None:
            time_in: datetime = datetime.strptime(self.time_in, "%H:%M:%S.%f") if self._time_in is not None else None
            time_out: datetime = datetime.strptime(self.time_out, "%H:%M:%S.%f") if self._time_out is not None else None

            return str(time_out - time_in) if self._time_in is not None and self._time_out is not None else None
        elif self._lunch_time_start is not None and self._lunch_time_stop is not None and self._time_in is not None and self._time_out is not None:
            # Apply lunch if lunch was taken
            lunch_time_start: str | None = datetime.strptime(self.lunch_time_start, "%H:%M:%S.%f")
            lunch_time_stop: str | None = datetime.strptime(self.lunch_time_stop, "%H:%M:%S.%f")

            time_in: str | None = datetime.strptime(self.time_in, "%H:%M:%S.%f")
            time_out: str | None = datetime.strptime(self.time_out, "%H:%M:%S.%f")

            return str((time_out - time_in) - (lunch_time_stop - lunch_time_start))
        
    def export_csv(self) -> None:
        try:
            with open(f"{self.date}.csv", 'w') as csv_file:
                writer = csv.DictWriter(csv_file, self.to_dict().keys())
                writer.writeheader()
                writer.writerow(self.to_dict())
        except IOError as err:
            print(f"Could not export {self.date}.csv: {err}")

    # Clear the clock.json file for new use.
    def clear_clock(self):
        self.date = None
        self.time_in = None
        self.time_out = None
        self.lunch_time_start = None
        self.lunch_time_stop = None
        self.is_clocked_in = False
        self.work_notes = None
        self.total_hours = None
        self.save()

        
    @classmethod
    def clocked_in(cls, clock_file: str) -> bool:
        try:
            with open(clock_file, 'r') as clock:
                clock_dict = json.loads(clock.read())

                if clock_dict['is_clocked_in']:
                    return True
                else:
                    return False
        except JSONDecodeError or FileNotFoundError as err:
            print("clock.json not found attempting to create...")
            cls.create_clockfile()
            print("clock.json created try clocking in again.")
            
    @classmethod
    def at_lunch(cls, clock_file: str) -> bool:
        with open(clock_file, 'r') as clock:
            clock_dict = json.loads(clock.read())

            if clock_dict['lunch_time_start'] and clock_dict['is_clocked_in'] == False:
                return True
            else:
                return False
            
    @classmethod
    def clockfile_detected(cls) -> bool:
        if path.exists('clock.json'):
            return True
        else:
            return False

    # Check if all the fields in clock.json are None/null 
    @classmethod
    def clock_cleared(cls) -> bool:
        try:
            if not cls.clockfile_detected():
                return True
            
            with open('clock.json', 'r') as clock_file:
                clock = json.loads(clock_file.read())

                for key in clock.keys():
                    if clock[key] is not None:
                        return False
                    else:
                        return True
        except IOError as err:
            print(f"There was a problem detecting if clock.json has been cleared: {err}")
        
    @classmethod
    def create_clockfile(cls) -> None:
        try:
            with open('clock.json', 'w') as clock_file:
                clock_file.write('')
        except IOError as err:
            print(f"Failed to create clock.json:{err}")

    # Return a dictionary representation of the current clock.json state
    @classmethod
    def dict_from_file(cls, clock_file: str) -> dict:
        try:
            with open(clock_file, 'r') as clock:
                clock_dict: dict = json.loads(clock.read())
                return clock_dict
        except FileNotFoundError:
            print("clock.json not found, creating")
            cls.create_clockfile()
        except IOError as err:
            print(f"Couldn't read clock.json file: {err}")
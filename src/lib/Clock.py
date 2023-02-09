from dataclasses import dataclass, field
from datetime import datetime, timedelta, time, date
# from typing import Optional

import json

@dataclass
class Clock:
    _date: date
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

    @property
    def time_in(self) -> str | None:
        return str(self._time_in) if self._time_in else None

    @property
    def time_out(self) -> str | None:
        return str(self._time_out) if self._time_out else None

    @property
    def lunch_time_start(self) -> str | None:
        return str(self._lunch_time_start) if self._lunch_time_start else None

    @property
    def lunch_time_stop(self) -> str | None:
        return str(self._lunch_time_stop) if self._lunch_time_stop else None

    @property
    def is_clocked_in(self) -> bool:
        return self._is_clocked_in

    @property
    def total_hours(self) -> int | None:
        return self._total_hours if self._total_hours is not None else None
    
    @property
    def lunch_total_time(self) -> int | None:
        return self._lunch_total_time if self._lunch_total_time is not None else None

    @property
    def work_notes(self) -> str | None:
        return self._work_notes if self._work_notes else None

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
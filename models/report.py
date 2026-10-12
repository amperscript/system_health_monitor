import getpass
from abc import ABC, abstractmethod
from datetime import datetime
from functools import total_ordering


class Report(ABC):
    @abstractmethod
    def finish(self):
        pass

    @abstractmethod
    def save(self, filename):
        pass


@total_ordering
class SessionReport(Report):
    def __init__(self, login=None, time_in=None, time_out=None):
        self._login = login or getpass.getuser()
        self._time_in = time_in or datetime.now().strftime('%d.%m.%Y %H:%M:%S')
        self._time_out = time_out

    @property
    def login(self):
        return self._login

    @login.setter
    def login(self, value):
        self._login = value

    @property
    def time_in(self):
        return self._time_in

    @time_in.setter
    def time_in(self, value):
        self._time_in = value

    @property
    def time_out(self):
        return self._time_out

    @time_out.setter
    def time_out(self, value):
        self._time_out = value

    def finish(self):
        self._time_out = datetime.now().strftime('%d.%m.%Y %H:%M:%S')

    @staticmethod
    def make_row(login, time_in, time_out):
        return f'| {login:<15} | {time_in:<19} | {time_out:<19} |'

    @staticmethod
    def make_border():
        return '+' + '-' * 61 + '+'

    @staticmethod
    def make_split():
        return '|' + '-' * 17 + '|' + '-' * 21 + '|' + '-' * 21 + '|'

    def save(self, filename='session_report.txt'):
        with open(filename, 'a', encoding='utf-8') as file:
            file.write(self.make_border() + '\n')
            file.write(self.make_row('login', 'time_in', 'time_out') + '\n')
            file.write(self.make_split() + '\n')
            file.write(str(self) + '\n')
            file.write(self.make_border() + '\n\n')

    def __str__(self):
        return self.make_row(self._login, self._time_in, str(self._time_out))

    def __repr__(self):
        return f'SessionReport({self._login}, {self._time_in}, {self._time_out})'

    def __eq__(self, other):
        if not isinstance(other, SessionReport):
            return False
        return self._login == other._login and self._time_in == other._time_in

    def __hash__(self):
        return hash((self._login, self._time_in))

    def __lt__(self, other):
        if not isinstance(other, SessionReport):
            return False
        return self._time_in < other._time_in
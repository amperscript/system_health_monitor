from abc import ABC, abstractmethod
from functools import total_ordering
from os import cpu_count

import psutil


@total_ordering
class Metric(ABC):
    def __init__(self, name, usage_percent):
        self.name = name
        self.usage_percent = usage_percent

    @property
    def name(self):
        return self._name

    @staticmethod
    def bytes_to_gb(value):
        return value / 1024 ** 3

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def usage_percent(self):
        return self._usage_percent

    @usage_percent.setter
    def usage_percent(self, value):
        if value < 0 or value > 100:
            raise ValueError('Процент использования должен быть от 0 до 100')
        self._usage_percent = value

    @property
    @abstractmethod
    def card_rows(self):
        pass

    @abstractmethod
    def describe(self):
        pass

    def __eq__(self, other):
        if not isinstance(other, Metric):
            return False
        return self.name == other.name and self.usage_percent == other.usage_percent

    def __hash__(self):
        return hash((self.name, self.usage_percent))

    def __lt__(self, other):
        if not isinstance(other, Metric):
            return False
        return self.usage_percent < other.usage_percent

    def __repr__(self):
        return f'{self.name}: {self.usage_percent}%'

    def __str__(self):
        return self.describe()


class CPUMetric(Metric):
    def __init__(self, usage_percent, cores):
        super().__init__('CPU', usage_percent)
        self.cores = cores

    @property
    def card_rows(self):
        return [
            (self.name, f'{self.usage_percent:.1f}', '%'),
            ('ядер', str(self.cores), '')
        ]

    @property
    def cores(self):
        return self._cores

    @cores.setter
    def cores(self, value):
        if value <= 0:
            raise ValueError('Некорректное число ядер')
        self._cores = value

    def describe(self):
        return f'{self.name}: {self.usage_percent}% ({self.cores} ядер)'


class RamMetric(Metric):
    def __init__(self, usage_percent, total_gb):
        super().__init__('RAM', usage_percent)
        self.total_gb = total_gb

    @property
    def total_gb(self):
        return self._total_gb

    @total_gb.setter
    def total_gb(self, value):
        if value <= 0:
            raise ValueError('Некорректное количество ГБ')
        self._total_gb = value

    @property
    def card_rows(self):
        return [
            (self.name, f'{self.total_gb:.1f}', 'ГБ'),
            ('занято', f'{self.usage_percent:.1f}', '%')
        ]

    def describe(self):
        return f'{self.name}: {self.total_gb:.1f} ГБ, занято {self.usage_percent}%'


class DiskMetric(Metric):
    def __init__(self, usage_percent, total_gb, free_gb):
        super().__init__('Диск', usage_percent)
        self.total_gb = total_gb
        self.free_gb = free_gb

    @property
    def total_gb(self):
        return self._total_gb

    @total_gb.setter
    def total_gb(self, value):
        if value <= 0:
            raise ValueError('Некорректное количество ГБ')
        self._total_gb = value

    @property
    def free_gb(self):
        return self._free_gb

    @free_gb.setter
    def free_gb(self, value):
        if value < 0:
            raise ValueError('Некорректное количество ГБ')
        self._free_gb = value

    @property
    def card_rows(self):
        return [
            (self.name, f'{self.usage_percent:.1f}', '%'),
            ('свободно', f'{self.free_gb:.1f}', 'ГБ')
        ]

    def describe(self):
        return f'{self.name}: {self.total_gb:.1f} ГБ, занято {self.usage_percent}%, свободное место на диске: {self.free_gb:.1f} ГБ'

class ProcessMetric(Metric):
    @property
    def card_rows(self):
        return [
            (self.name, f'{self.usage_percent:.1f}', '%')
        ]

    def describe(self):
        return f'{self.name}. Занимаемая память: {self.usage_percent}'


class AbstractMetricList(ABC):
    @abstractmethod
    def add(self, metric):
        pass

    @abstractmethod
    def get(self, name):
        pass

    @abstractmethod
    def get_all(self):
        pass


@total_ordering
class MetricList(AbstractMetricList):
    def __init__(self):
        self.metrics = []

    @property
    def metrics(self):
        return self._metrics

    @metrics.setter
    def metrics(self, value):
        self._metrics = value

    def add(self, metric):
        self.metrics.append(metric)

    def get(self, name):
        for metric in self.metrics:
            if metric.name == name:
                return metric
        return None

    def get_all(self):
        return self.metrics

    def __len__(self):
        return len(self.metrics)

    def __eq__(self, other):
        if not isinstance(other, MetricList):
            return False
        return self.metrics == other.metrics

    def __hash__(self):
        return hash(tuple(self.metrics))

    def __lt__(self, other):
        if not isinstance(other, MetricList):
            return False
        return self.metrics < other.metrics

    def __repr__(self):
        return f'MetricList({self.metrics!r})'

    def __str__(self):
        return '\n'.join(str(metric) for metric in self.metrics)

    def read_processes(self):
        processes = []
        for p in psutil.process_iter():
            try:
                processes.append(ProcessMetric(p.name(), p.memory_percent()))
            except psutil.Error:
                continue
        processes.sort(reverse=True)
        for process in processes[:7]:
            self.add(process)

    def read_system(self):
        self.metrics = []

        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')

        self.add(CPUMetric(psutil.cpu_percent(interval=0.5), cpu_count()))
        self.add(RamMetric(memory.percent, RamMetric.bytes_to_gb(memory.total)))
        self.add(DiskMetric(disk.percent, DiskMetric.bytes_to_gb(disk.total), DiskMetric.bytes_to_gb(disk.free)))

        self.read_processes()

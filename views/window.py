from functools import total_ordering

import flet as ft

from models.metrics import MetricList, ProcessMetric
from models.report import SessionReport


@total_ordering
class MetricCard(ft.Container):
    def __init__(self, metric):
        super().__init__()
        self.rows = ft.Column(spacing=8)
        self.bar = ft.ProgressBar(border_radius=24, height=4)
        self.content = ft.Column(
            [self.rows, ft.Container(content=self.bar, padding=ft.Padding(0, 10, 0, 0))],
            spacing=8, horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )
        self.width = 200
        self.height = 140
        self.padding = 24
        self.border_radius = 24
        self.bgcolor = ft.Colors.GREY_100
        self.set_metric(metric)

    @property
    def metric(self):
        return self._metric

    @metric.setter
    def metric(self, value):
        self._metric = value

    @property
    def rows(self):
        return self._rows

    @rows.setter
    def rows(self, value):
        self._rows = value

    @property
    def bar(self):
        return self._bar

    @bar.setter
    def bar(self, value):
        self._bar = value

    def set_metric(self, metric):
        self.metric = metric
        self.bar.value = metric.usage_percent / 100
        self.rows.controls = [self.info_row(name, value, unit) for name, value, unit in metric.card_rows]

    @staticmethod
    def info_row(name, value, unit):
        return ft.Row([
            ft.Text(name, color=ft.Colors.GREY_900),
            ft.Row(
                [ft.Text(value, color=ft.Colors.BLUE_900, weight=ft.FontWeight.BOLD),
                 ft.Text(unit, color=ft.Colors.GREY_500),
                 ], spacing=2,
            )
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

    def __eq__(self, other):
        return self is other

    def __lt__(self, other):
        if not isinstance(other, MetricCard):
            return False
        return self.metric.usage_percent < other.metric.usage_percent

    def __repr__(self):
        return f'MetricCard({self.metric!r})'

    def __str__(self):
        return f'Карточка: {self.metric}'


@total_ordering
class Monitor(ft.Container):
    def __init__(self):
        super().__init__()
        self.width = 632

        metrics = MetricList()
        metrics.read_system()
        self.metrics = metrics

        self.cpu = MetricCard(metrics.get('CPU'))
        self.ram = MetricCard(metrics.get('RAM'))
        self.disk = MetricCard(metrics.get('Диск'))
        self.proc_list = ProcessList(self.get_processes(metrics))
        self.button = ft.Button('Обновить', on_click=self.on_refresh)

        self.content = ft.Column([
            ft.Row([self.button], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Row(
                [
                    ft.Icon(ft.Icons.COMPUTER, size=24, color=ft.Colors.BLUE_900),
                    ft.Text('Система', size=20, weight=ft.FontWeight.BOLD),
                ],
                spacing=8,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),

            ft.Row([
                self.cpu,
                self.ram,
                self.disk,
            ], spacing=16),
            ft.Row(
                [
                    ft.Icon(ft.Icons.MEMORY, size=24, color=ft.Colors.BLUE_900),
                    ft.Text('Топ процессов', size=20, weight=ft.FontWeight.BOLD),
                ],
                spacing=8,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),

            self.proc_list.make_panel(),
        ], horizontal_alignment=ft.CrossAxisAlignment.STRETCH)

    @property
    def metrics(self):
        return self._metrics

    @metrics.setter
    def metrics(self, value):
        self._metrics = value

    @property
    def cpu(self):
        return self._cpu

    @cpu.setter
    def cpu(self, value):
        self._cpu = value

    @property
    def ram(self):
        return self._ram

    @ram.setter
    def ram(self, value):
        self._ram = value

    @property
    def disk(self):
        return self._disk

    @disk.setter
    def disk(self, value):
        self._disk = value

    @property
    def proc_list(self):
        return self._proc_list

    @proc_list.setter
    def proc_list(self, value):
        self._proc_list = value

    @property
    def button(self):
        return self._button

    @button.setter
    def button(self, value):
        self._button = value

    def show_metrics(self):
        self.cpu.set_metric(self.metrics.get('CPU'))
        self.ram.set_metric(self.metrics.get('RAM'))
        self.disk.set_metric(self.metrics.get('Диск'))
        self.proc_list.update_processes(self.get_processes(self.metrics))
        self.update()

    def on_refresh(self, e):
        self.metrics.read_system()
        self.show_metrics()

    @staticmethod
    def get_processes(metrics):
        result = []
        for m in metrics.get_all():
            if isinstance(m, ProcessMetric):
                result.append(m)
        return result

    def __eq__(self, other):
        return self is other

    def __lt__(self, other):
        if not isinstance(other, Monitor):
            return False
        return len(self.metrics) < len(other.metrics)

    def __repr__(self):
        return f'Monitor({self.metrics!r})'

    def __str__(self):
        return f'Монитор: {self.metrics}'


@total_ordering
class ProcessList(ft.ListView):
    def __init__(self, processes):
        super().__init__(spacing=0, divider_thickness=1, height=280, width=624)
        self.processes = processes

    @property
    def processes(self):
        return self._processes

    @processes.setter
    def processes(self, value):
        self._processes = value
        self.controls.clear()
        for p in value:
            self.controls.append(self.make_row(p))

    def make_header(self):
        return ft.Container(
            content=ft.Row([
                ft.Text('Имя процесса', expand=True, size=12,
                        color=ft.Colors.GREY_700, weight=ft.FontWeight.W_500),
                ft.Text('% памяти', width=80, text_align=ft.TextAlign.RIGHT, size=12,
                        color=ft.Colors.GREY_700, weight=ft.FontWeight.W_500),
            ], spacing=10),
            padding=ft.Padding(16, 6, 16, 6),
        )

    def make_row(self, p):
        return ft.Container(
            content=ft.Row([
                ft.Text(p.name, expand=True, size=14),
                ft.Text(f'{p.usage_percent:.1f}%', width=80,
                        text_align=ft.TextAlign.RIGHT, size=14),
            ], spacing=10),
            padding=ft.Padding(16, 8, 16, 8),
            margin=ft.Margin(0, 4, 0, 0),
            border_radius=16,
            bgcolor=ft.Colors.GREY_100,
        )

    def make_panel(self):
        return ft.Container(
            content=ft.Column([self.make_header(), self], spacing=4),
            border_radius=16,
            padding=ft.Padding(4, 4, 4, 4),
        )

    def update_processes(self, processes):
        self.processes = processes

    def __len__(self):
        return len(self.processes)

    def __eq__(self, other):
        return self is other

    def __lt__(self, other):
        if not isinstance(other, ProcessList):
            return False
        return len(self) < len(other)

    def __repr__(self):
        return f'ProcessList({len(self)} процессов)'

    def __str__(self):
        return f'Топ процессов: {len(self)}'


class App:
    def __init__(self, page: ft.Page):
        self.page = page
        self.report = SessionReport()

    @property
    def page(self):
        return self._page

    @page.setter
    def page(self, value):
        self._page = value

    @property
    def report(self):
        return self._report

    @report.setter
    def report(self, value):
        self._report = value

    def view(self):
        self.page.title = 'Проверка состояния компьютера'
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.spacing = 50
        self.page.vertical_alignment = ft.MainAxisAlignment.CENTER
        self.page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

        self.page.window.prevent_close = True
        self.page.window.on_event = self.on_window_event

        self.page.add(ft.SafeArea(content=ft.Row(
            controls=[Monitor()],
            alignment=ft.MainAxisAlignment.CENTER,
        )
        ))

    async def on_window_event(self, e):
        if e.type == ft.WindowEventType.CLOSE:
            await self.close()

    async def close(self):
        self.report.finish()
        self.report.save()
        await self.page.window.destroy()

    def __eq__(self, other):
        if not isinstance(other, App):
            return False
        return self.report == other.report

    def __hash__(self):
        return hash(self.report)

    def __lt__(self, other):
        if not isinstance(other, App):
            return False
        return self.report < other.report

    def __repr__(self):
        return f'App({self.report!r})'

    def __str__(self):
        return f'Приложение: {self.report}'

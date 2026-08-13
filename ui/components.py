import json
import pathlib

import flet as ft

from i18n import tr


# ---------------------------------------------------------------------------
#  ГЛОБАЛЬНАЯ КОНСОЛЬ (LOG VIEWER)
# ---------------------------------------------------------------------------
class LogViewer(ft.UserControl):
    """Глобальная консоль с тёмной темой и автопрокруткой."""

    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        self.list_view = ft.ListView(expand=True, spacing=2, auto_scroll=True, padding=5)

    def build(self):
        return ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Text(tr("console_title"), size=12,
                                    weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_400),
                            ft.IconButton(ft.Icons.DELETE_OUTLINE, icon_size=16,
                                          tooltip=tr("console_clear"), on_click=self.clear),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    self.list_view,
                ],
                expand=True,
                spacing=0,
            ),
            height=180,
            bgcolor=ft.Colors.BLACK87,
            border=ft.border.all(1, ft.Colors.GREY_800),
            border_radius=8,
            padding=10,
        )

    def log(self, message: str, level: str = "INFO"):
        color_map = {
            "INFO": ft.Colors.GREY_300,
            "SUCCESS": ft.Colors.GREEN_400,
            "WARNING": ft.Colors.AMBER_400,
            "ERROR": ft.Colors.RED_400,
        }
        color = color_map.get(level, ft.Colors.GREY_300)
        self.list_view.controls.append(
            ft.Text(f"[{level}] {message}", color=color, selectable=True,
                    font_family="Consolas", size=12)
        )
        self.update()

    def clear(self, e):
        self.list_view.controls.clear()
        self.update()


# ---------------------------------------------------------------------------
#  МЕНЕДЖЕР НАСТРОЕК (settings.json)
# ---------------------------------------------------------------------------
class SettingsManager:
    """Хранение API_ID / API_HASH / phone / language локально в settings.json."""

    def __init__(self, settings_path: str = "settings.json"):
        self.path = pathlib.Path(settings_path)
        self.data = self._load()

    def _load(self) -> dict:
        if self.path.exists():
            try:
                return json.loads(self.path.read_text(encoding="utf-8"))
            except Exception:
                return {}
        return {}

    def get(self, key: str, default=None):
        return self.data.get(key, default)

    def set(self, key: str, value):
        self.data[key] = value
        self._save()

    def _save(self):
        self.path.write_text(
            json.dumps(self.data, indent=2, ensure_ascii=False), encoding="utf-8"
        )


# ---------------------------------------------------------------------------
#  КНОПКА ВЫБОРА ПАПКИ
# ---------------------------------------------------------------------------
class FolderPickerButton(ft.UserControl):
    """Выбор папки через ft.FilePicker."""

    def __init__(self, page: ft.Page, label: str, on_result=None):
        super().__init__()
        self.page = page
        self.label = label
        self.on_result = on_result
        self.selected_path = None
        self.text_field = ft.TextField(
            read_only=True, expand=True, label=label, hint_text=tr("no_folder")
        )
        self.file_picker = ft.FilePicker(on_result=self._on_folder_picked)
        self.page.overlay.append(self.file_picker)

    def build(self):
        return ft.Row(
            [
                self.text_field,
                ft.ElevatedButton(
                    tr("pick_folder"),
                    icon=ft.Icons.FOLDER_OPEN,
                    on_click=lambda e: self.file_picker.get_directory_path(
                        dialog_title=self.label
                    ),
                ),
            ],
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

    def _on_folder_picked(self, e: ft.FilePickerResultEvent):
        if e.path:
            self.selected_path = pathlib.Path(e.path)
            self.text_field.value = str(self.selected_path)
            self.update()
            if self.on_result:
                self.on_result(self.selected_path)


# ---------------------------------------------------------------------------
#  КНОПКА ВЫБОРА ФАЙЛА
# ---------------------------------------------------------------------------
class FilePickerButton(ft.UserControl):
    """Выбор файла через ft.FilePicker."""

    def __init__(self, page: ft.Page, label: str, extensions=None, on_result=None):
        super().__init__()
        self.page = page
        self.label = label
        self.on_result = on_result
        self.extensions = extensions
        self.selected_path = None
        self.text_field = ft.TextField(
            read_only=True, expand=True, label=label, hint_text=tr("no_file")
        )
        self.file_picker = ft.FilePicker(on_result=self._on_file_picked)
        self.page.overlay.append(self.file_picker)

    def build(self):
        return ft.Row(
            [
                self.text_field,
                ft.ElevatedButton(
                    tr("pick_file"),
                    icon=ft.Icons.DESCRIPTION,
                    on_click=lambda e: self.file_picker.pick_files(
                        dialog_title=self.label,
                        allowed_extensions=self.extensions,
                    ),
                ),
            ],
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

    def _on_file_picked(self, e: ft.FilePickerResultEvent):
        if e.files:
            self.selected_path = pathlib.Path(e.files[0].path)
            self.text_field.value = str(self.selected_path)
            self.update()
            if self.on_result:
                self.on_result(self.selected_path)


# ---------------------------------------------------------------------------
#  КНОПКА «?» СО ВСПЛЫВАЮЩЕЙ ИНСТРУКЦИЕЙ
# ---------------------------------------------------------------------------
class HelpButton(ft.UserControl):
    """Кнопка «?» — открывает всплывающую инструкцию для пользователя."""

    def __init__(self, page: ft.Page, title: str, steps: list):
        super().__init__()
        self.page = page
        self.title = title
        self.steps = steps

    def build(self):
        return ft.IconButton(
            ft.Icons.HELP_OUTLINE,
            tooltip=tr("help_tooltip"),
            icon_color=ft.Colors.BLUE_300,
            on_click=self.show,
        )

    def show(self, e):
        def close(ev):
            dlg.open = False
            self.page.update()

        dlg = ft.AlertDialog(
            modal=False,
            title=ft.Text(self.title),
            content=ft.Container(
                content=ft.Column(
                    [ft.Text(s, size=13, selectable=True) for s in self.steps],
                    spacing=10,
                    scroll=ft.ScrollMode.AUTO,
                ),
                width=560,
                height=440,
            ),
            actions=[ft.TextButton(tr("help_ok"), on_click=close)],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self.page.open(dlg)
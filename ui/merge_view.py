import pathlib
import threading

import flet as ft

from core.merge import merge_json_files
from i18n import tr
from ui.components import FolderPickerButton, HelpButton, LogViewer


class MergeView(ft.UserControl):
    """Экран «Слияние»: объединение messages*.json в один result.json."""

    def __init__(self, page: ft.Page, log_viewer: LogViewer):
        super().__init__()
        self.page = page
        self.log = log_viewer

        self.folder_picker = FolderPickerButton(page, tr("merge_folder"))

        self.progress_bar = ft.ProgressBar(
            visible=False, color=ft.Colors.BLUE_400, bgcolor=ft.Colors.GREY_800
        )
        self.status_text = ft.Text(tr("merge_ready"), size=12, color=ft.Colors.GREY_500)

        self.btn_start = ft.ElevatedButton(
            tr("merge_start"),
            icon=ft.Icons.PLAY_ARROW,
            on_click=self.start_merge,
        )

    def build(self):
        return ft.Column(
            [
                ft.Row(
                    [
                        ft.Text(tr("merge_title"), size=24, weight=ft.FontWeight.BOLD),
                        HelpButton(self.page, tr("merge_help_title"), tr("instr_merge")),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                ft.Divider(),

                ft.Text(tr("merge_desc"), size=12, color=ft.Colors.GREY_500),
                self.folder_picker,

                ft.Divider(),

                ft.Row(
                    [self.btn_start, self.status_text],
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                self.progress_bar,
            ],
            spacing=15,
            expand=True,
            scroll=ft.ScrollMode.AUTO,
        )

    def start_merge(self, e):
        folder = self.folder_picker.selected_path
        if not folder:
            self.snack(tr("merge_err_folder"), ft.Colors.RED_700)
            return

        self.btn_start.disabled = True
        self.progress_bar.visible = True
        self.progress_bar.value = 0.05
        self.status_text.value = tr("merge_running")
        self.safe_update()

        self.log.log(f"🚀 Merge: {folder}", "INFO")
        threading.Thread(target=self._run_merge, args=(folder,), daemon=True).start()

    def _run_merge(self, folder: pathlib.Path):
        try:
            success = merge_json_files(folder, log_callback=self.log.log)

            if success:
                self.progress_bar.value = 1.0
                self.status_text.value = tr("merge_done")
                self.snack(tr("merge_done_snack"), ft.Colors.GREEN_700)
            else:
                self.status_text.value = tr("merge_err")
                self.snack(tr("merge_err_snack"), ft.Colors.RED_700)
        except Exception as ex:
            self.status_text.value = tr("err_generic", err=ex)
            self.log.log(f"❌ Критическая ошибка слияния: {ex}", "ERROR")
            self.snack(tr("err_generic", err=ex), ft.Colors.RED_700)
        finally:
            self.progress_bar.visible = False
            self.btn_start.disabled = False
            self.safe_update()

    def snack(self, message: str, color: str):
        self.log.log(message, "ERROR" if "❌" in message else "WARNING")
        self.page.open(ft.SnackBar(content=ft.Text(message), bgcolor=color))

    def safe_update(self):
        try:
            self.update()
        except Exception:
            try:
                self.page.update()
            except Exception:
                pass
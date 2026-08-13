import pathlib
import shutil
import threading

import flet as ft

from core.converter import convert_html_export
from i18n import tr
from ui.components import FolderPickerButton, HelpButton, LogViewer


class ConverterView(ft.UserControl):
    """Экран «Конвертер»: конвертация HTML-бэкапа Telegram в JSON."""

    def __init__(self, page: ft.Page, log_viewer: LogViewer):
        super().__init__()
        self.page = page
        self.log = log_viewer

        # ------------------------- элементы формы -------------------------
        self.folder_picker = FolderPickerButton(page, tr("conv_folder"))
        self.save_dir_picker = FolderPickerButton(page, tr("conv_save"))
        self.chat_id_field = ft.TextField(
            label=tr("conv_chatid"),
            hint_text=tr("conv_chatid_hint"),
            keyboard_type=ft.KeyboardType.NUMBER,
            width=220,
        )

        # ------------------------- sender_map -------------------------
        self.sender_map_rows: list = []
        self.sender_map_container = ft.Column(spacing=6)

        # ------------------------- прогресс -------------------------
        self.progress_bar = ft.ProgressBar(
            visible=False, color=ft.Colors.BLUE_400, bgcolor=ft.Colors.GREY_800
        )
        self.status_text = ft.Text(tr("conv_ready"), size=12, color=ft.Colors.GREY_500)

        self.btn_start = ft.ElevatedButton(
            tr("conv_start"),
            icon=ft.Icons.PLAY_ARROW,
            on_click=self.start_conversion,
        )

    # ============================== BUILD ==============================
    def build(self):
        if not self.sender_map_rows:
            self._append_row(self._make_row())

        return ft.Column(
            [
                ft.Row(
                    [
                        ft.Text(tr("conv_title"), size=24, weight=ft.FontWeight.BOLD),
                        HelpButton(self.page, tr("conv_help_title"), tr("instr_converter")),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                ft.Divider(),

                self.folder_picker,

                # picker обёрнут в Container(expand=True), чтобы не «улетал» в угол
                ft.Row(
                    [
                        self.chat_id_field,
                        ft.Container(content=self.save_dir_picker, expand=True),
                    ],
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),

                ft.Divider(),

                ft.Row(
                    [
                        ft.Text(tr("conv_map_title"), size=16, weight=ft.FontWeight.BOLD),
                        ft.IconButton(
                            ft.Icons.ADD_CIRCLE_OUTLINE,
                            tooltip=tr("conv_map_add"),
                            on_click=self.add_sender_row,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                ft.Text(tr("conv_map_hint"), size=12, color=ft.Colors.GREY_500),
                self.sender_map_container,

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

    # ============================ sender_map ============================
    def _make_row(self, name: str = "", uid: str = "") -> dict:
        tf_name = ft.TextField(label=tr("conv_map_name"), value=name, expand=True, dense=True)
        tf_uid = ft.TextField(label=tr("conv_map_uid"), value=uid, expand=True, dense=True)
        row_data = {"name": tf_name, "uid": tf_uid}

        def on_remove(e, rd=row_data):
            if rd in self.sender_map_rows:
                self.sender_map_rows.remove(rd)
            if rd["container"] in self.sender_map_container.controls:
                self.sender_map_container.controls.remove(rd["container"])
            self.safe_update()

        row_data["container"] = ft.Row(
            [
                tf_name,
                tf_uid,
                ft.IconButton(
                    ft.Icons.DELETE_OUTLINE,
                    icon_color=ft.Colors.RED_400,
                    tooltip=tr("conv_map_remove"),
                    on_click=on_remove,
                ),
            ],
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )
        return row_data

    def _append_row(self, rd: dict):
        self.sender_map_rows.append(rd)
        self.sender_map_container.controls.append(rd["container"])

    def add_sender_row(self, e=None):
        self._append_row(self._make_row())
        self.safe_update()

    def get_sender_map(self) -> dict:
        result = {}
        for rd in self.sender_map_rows:
            name = (rd["name"].value or "").strip()
            uid = (rd["uid"].value or "").strip()
            if name and uid:
                result[name] = uid
        return result

    # ============================== запуск ==============================
    def start_conversion(self, e):
        export_dir = self.folder_picker.selected_path
        save_dir = self.save_dir_picker.selected_path
        chat_id_str = (self.chat_id_field.value or "").strip()

        if not export_dir:
            self.snack(tr("conv_err_folder"), ft.Colors.RED_700)
            return
        if not chat_id_str.isdigit():
            self.snack(tr("conv_err_chatid"), ft.Colors.RED_700)
            return

        sender_map = self.get_sender_map()
        if not sender_map:
            self.snack(tr("conv_warn_map"), ft.Colors.AMBER_700)

        self.btn_start.disabled = True
        self.progress_bar.visible = True
        self.progress_bar.value = 0
        self.status_text.value = tr("conv_starting")
        self.safe_update()

        self.log.log(f"🚀 {export_dir}", "INFO")

        threading.Thread(
            target=self._run_conversion,
            args=(export_dir, int(chat_id_str), sender_map, save_dir),
            daemon=True,
        ).start()

    # ------------------------ фоновый поток ------------------------
    def _run_conversion(self, export_dir, chat_id, sender_map, save_dir):
        try:
            def on_progress(progress: float):
                self.progress_bar.value = progress
                self.status_text.value = tr("conv_progress", pct=int(progress * 100))
                self.safe_update()

            success = convert_html_export(
                export_dir=export_dir,
                chat_id=chat_id,
                sender_map=sender_map,
                log_callback=self.log.log,
                progress_callback=on_progress,
            )

            if not success:
                self.status_text.value = tr("conv_err")
                self.snack(tr("conv_err"), ft.Colors.RED_700)
                return

            if save_dir and save_dir != export_dir:
                copied = 0
                for jf in sorted(export_dir.glob("messages*.json")):
                    shutil.copy2(jf, save_dir / jf.name)
                    copied += 1
                self.log.log(tr("conv_copied", n=copied, path=save_dir), "SUCCESS")

            self.progress_bar.value = 1.0
            self.status_text.value = tr("conv_done")
            self.snack(tr("conv_done_snack"), ft.Colors.GREEN_700)

        except Exception as ex:
            self.status_text.value = tr("err_generic", err=ex)
            self.log.log(f"❌ {ex}", "ERROR")
            self.snack(tr("err_generic", err=ex), ft.Colors.RED_700)

        finally:
            self.progress_bar.visible = False
            self.btn_start.disabled = False
            self.safe_update()

    # ============================ хелперы ============================
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
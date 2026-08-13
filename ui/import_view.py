import math
import pathlib
import threading

import flet as ft

from core.auth import telethon_auth_flow
from core.importer import import_history
from i18n import tr
from ui.components import FolderPickerButton, HelpButton, LogViewer, SettingsManager


class ImportView(ft.UserControl):
    """Экран «Импорт»: загрузка result.json и медиа в Telegram через Telethon."""

    def __init__(self, page: ft.Page, log_viewer: LogViewer):
        super().__init__()
        self.page = page
        self.log = log_viewer
        self.settings = SettingsManager("settings.json")

        # ------------------------- API credentials -------------------------
        self.api_id_field = ft.TextField(
            label="API ID",
            value=str(self.settings.get("api_id", "")),
            hint_text=tr("imp_apiid_hint"),
            width=200,
            keyboard_type=ft.KeyboardType.NUMBER,
        )
        self.api_hash_field = ft.TextField(
            label="API Hash",
            value=self.settings.get("api_hash", ""),
            hint_text=tr("imp_apihash_hint"),
            width=350,
            password=True,
            can_reveal_password=True,
        )
        self.phone_field = ft.TextField(
            label=tr("imp_phone"),
            value=self.settings.get("phone", ""),
            hint_text=tr("imp_phone_hint"),
            width=200,
        )

        # ------------------------- параметры импорта -------------------------
        self.folder_picker = FolderPickerButton(page, tr("imp_folder"))
        self.peer_field = ft.TextField(
            label=tr("imp_peer"),
            hint_text=tr("imp_peer_hint"),
            expand=True,
        )
        self.test_mode_switch = ft.Switch(label=tr("imp_test"), value=False)
        self.only_first_field = ft.TextField(label=tr("imp_onlyN"), value="", width=320)

        # ------------------------- прогресс -------------------------
        self.progress_bar = ft.ProgressBar(
            visible=False, color=ft.Colors.GREEN_400, bgcolor=ft.Colors.GREY_800
        )
        self.status_text = ft.Text(tr("imp_ready"), size=12, color=ft.Colors.GREY_500)

        self.btn_start = ft.ElevatedButton(
            tr("imp_start"),
            icon=ft.Icons.CLOUD_UPLOAD,
            on_click=self.start_import,
        )
        self.btn_save_settings = ft.TextButton(
            tr("imp_save"), icon=ft.Icons.SAVE, on_click=self.save_settings
        )
        self.btn_help = HelpButton(self.page, tr("imp_help_title"), tr("instr_import"))

    # ============================== BUILD ==============================
    def build(self):
        return ft.Column(
            [
                ft.Row(
                    [
                        ft.Text(tr("imp_title"), size=24, weight=ft.FontWeight.BOLD),
                        self.btn_help,
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                ft.Divider(),

                ft.Text(tr("imp_api_title"), size=16, weight=ft.FontWeight.BOLD),
                ft.Text(tr("imp_api_desc"), size=12, color=ft.Colors.GREY_500),
                ft.Row(
                    [self.api_id_field, self.api_hash_field, self.phone_field],
                    wrap=True,
                ),
                self.btn_save_settings,

                ft.Divider(),

                ft.Text(tr("imp_params"), size=16, weight=ft.FontWeight.BOLD),
                self.folder_picker,
                self.peer_field,
                ft.Row(
                    [self.test_mode_switch, self.only_first_field],
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),

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

    # ============================== настройки ==============================
    def save_settings(self, e):
        self.settings.set("api_id", (self.api_id_field.value or "").strip())
        self.settings.set("api_hash", (self.api_hash_field.value or "").strip())
        self.settings.set("phone", (self.phone_field.value or "").strip())
        self.log.log(tr("imp_saved"), "SUCCESS")
        self.page.open(
            ft.SnackBar(content=ft.Text(tr("imp_saved")), bgcolor=ft.Colors.GREEN_700)
        )

    # ============================== запуск ==============================
    def start_import(self, e):
        api_id_str = (self.api_id_field.value or "").strip()
        api_hash = (self.api_hash_field.value or "").strip()
        phone = (self.phone_field.value or "").strip()
        export_dir = self.folder_picker.selected_path
        peer_id = (self.peer_field.value or "").strip()

        if not api_id_str.isdigit():
            self.snack(tr("imp_err_apiid"), ft.Colors.RED_700)
            return
        if not api_hash:
            self.snack(tr("imp_err_apihash"), ft.Colors.RED_700)
            return
        if not phone:
            self.snack(tr("imp_err_phone"), ft.Colors.RED_700)
            return
        if not export_dir:
            self.snack(tr("imp_err_folder"), ft.Colors.RED_700)
            return
        if not peer_id:
            self.snack(tr("imp_err_peer"), ft.Colors.RED_700)
            return

        only_first_n = math.inf
        only_str = (self.only_first_field.value or "").strip()
        if only_str:
            try:
                only_first_n = float(only_str)
            except ValueError:
                self.snack(tr("imp_err_onlyN"), ft.Colors.RED_700)
                return

        self.btn_start.disabled = True
        self.progress_bar.visible = True
        self.progress_bar.value = 0
        self.status_text.value = tr("imp_init")
        self.safe_update()

        self.log.log(f"🚀 {export_dir}", "INFO")
        self.log.log(f"🎯 {peer_id}", "INFO")

        threading.Thread(
            target=self._run_import,
            args=(export_dir, peer_id, int(api_id_str), api_hash, phone,
                  self.test_mode_switch.value, only_first_n),
            daemon=True,
        ).start()

    # ------------------------ фоновый поток ------------------------
    def _run_import(self, export_dir, peer_id, api_id, api_hash, phone,
                    test_only, only_first_n):
        try:
            def on_progress(progress: float, status: str = ""):
                self.progress_bar.value = progress
                if status:
                    # status = чистое имя файла из core/importer.py
                    self.status_text.value = tr("imp_uploading", name=status)
                self.safe_update()

            def auth_callback(client):
                # перехват кода/2FA через ft.AlertDialog (core/auth.py)
                telethon_auth_flow(self.page, client, phone, log_callback=self.log.log)

            success = import_history(
                path=export_dir,
                peer_id=peer_id,
                api_id=api_id,
                api_hash=api_hash,
                auth_callback=auth_callback,
                log_callback=self.log.log,
                progress_callback=on_progress,
                test_only=test_only,
                only_first_n=only_first_n,
            )

            if success:
                self.progress_bar.value = 1.0
                self.status_text.value = tr("imp_done")
                self.snack(tr("imp_done_snack"), ft.Colors.GREEN_700)
            else:
                self.status_text.value = tr("imp_err")
                self.snack(tr("imp_err_snack"), ft.Colors.RED_700)

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
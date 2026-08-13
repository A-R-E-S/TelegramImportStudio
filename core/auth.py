import threading
from typing import Callable, Optional

import flet as ft
from telethon.errors import SessionPasswordNeededError
from telethon.sync import TelegramClient

from i18n import tr


def telethon_auth_flow(
    page: ft.Page,
    client: TelegramClient,
    phone: str,
    log_callback: Optional[Callable[[str, str], None]] = None,
) -> bool:
    """
    Авторизация Telethon в GUI: перехватывает запрос кода/2FA и показывает
    модальные ft.AlertDialog вместо консольного input().

    ВЫЗЫВАЕТСЯ ИЗ ФОНОВОГО ПОТОКА (внутри import_history).
    Блокирует поток через threading.Event до ввода данных пользователем.
    """
    try:
        if client.is_user_authorized():
            if log_callback:
                log_callback("✅ Сессия уже авторизована.", "SUCCESS")
            return True

        if log_callback:
            log_callback(f"📤 Отправка кода подтверждения на {phone}...", "INFO")
        client.send_code_request(phone)

        # ---------------- ШАГ 1: код из Telegram / СМС ----------------
        code_event = threading.Event()
        code_result = {"value": None, "cancelled": False}

        def show_code_dialog():
            def on_submit(e):
                code_result["value"] = tf.value.strip()
                dlg.open = False
                page.update()
                code_event.set()

            def on_cancel(e):
                code_result["cancelled"] = True
                dlg.open = False
                page.update()
                code_event.set()

            tf = ft.TextField(
                label=tr("auth_code_label"),
                autofocus=True,
                keyboard_type=ft.KeyboardType.NUMBER,
                width=250,
                on_submit=on_submit,
            )
            dlg = ft.AlertDialog(
                modal=True,
                title=ft.Text(tr("auth_code_title")),
                content=ft.Column(
                    [ft.Text(tr("auth_code_desc")), tf],
                    tight=True,
                    spacing=10,
                ),
                actions=[
                    ft.TextButton(tr("auth_cancel"), on_click=on_cancel),
                    ft.ElevatedButton(tr("auth_login"), on_click=on_submit),
                ],
                actions_alignment=ft.MainAxisAlignment.END,
            )
            page.open(dlg)

        page.run_thread(show_code_dialog)
        code_event.wait()  # блокируем фоновый поток до ввода

        if code_result["cancelled"]:
            raise RuntimeError("Пользователь отменил авторизацию.")
        if not code_result["value"]:
            raise RuntimeError("Код не был введён.")

        try:
            client.sign_in(phone, code_result["value"])
            if log_callback:
                log_callback("✅ Вход по коду выполнен успешно.", "SUCCESS")
            return True
        except SessionPasswordNeededError:
            pass

        # ---------------- ШАГ 2: пароль 2FA ----------------
        if log_callback:
            log_callback("🔑 Требуется пароль двухфакторной аутентификации (2FA).", "WARNING")

        pwd_event = threading.Event()
        pwd_result = {"value": None, "cancelled": False}

        def show_pwd_dialog():
            def on_submit(e):
                pwd_result["value"] = tf.value
                dlg.open = False
                page.update()
                pwd_event.set()

            def on_cancel(e):
                pwd_result["cancelled"] = True
                dlg.open = False
                page.update()
                pwd_event.set()

            tf = ft.TextField(
                label=tr("auth_pwd_label"),
                password=True,
                can_reveal_password=True,
                autofocus=True,
                width=250,
                on_submit=on_submit,
            )
            dlg = ft.AlertDialog(
                modal=True,
                title=ft.Text(tr("auth_pwd_title")),
                content=ft.Column(
                    [ft.Text(tr("auth_pwd_desc")), tf],
                    tight=True,
                    spacing=10,
                ),
                actions=[
                    ft.TextButton(tr("auth_cancel"), on_click=on_cancel),
                    ft.ElevatedButton(tr("auth_confirm"), on_click=on_submit),
                ],
                actions_alignment=ft.MainAxisAlignment.END,
            )
            page.open(dlg)

        page.run_thread(show_pwd_dialog)
        pwd_event.wait()

        if pwd_result["cancelled"]:
            raise RuntimeError("Пользователь отменил ввод 2FA-пароля.")
        if not pwd_result["value"]:
            raise RuntimeError("Пароль 2FA не был введён.")

        client.sign_in(password=pwd_result["value"])
        if log_callback:
            log_callback("✅ Вход по 2FA-паролю выполнен успешно.", "SUCCESS")
        return True

    except Exception as e:
        if log_callback:
            log_callback(f"❌ Ошибка авторизации: {str(e)}", "ERROR")
        raise
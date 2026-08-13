import flet as ft

from i18n import LANGUAGES, get_language, set_language, tr
from ui.components import LogViewer, SettingsManager
from ui.converter_view import ConverterView
from ui.merge_view import MergeView
from ui.import_view import ImportView


def main(page: ft.Page):
    settings = SettingsManager("settings.json")
    set_language(settings.get("language", "ru"))

    page.title = "Telegram Import Studio"
    page.theme_mode = ft.ThemeMode.DARK
    page.window.width = 1100
    page.window.height = 750
    page.padding = 0
    page.spacing = 0

    # Глобальная консоль
    log_viewer = LogViewer(page)

    # Экраны
    views = {
        "converter": ConverterView(page, log_viewer),
        "merge": MergeView(page, log_viewer),
        "import": ImportView(page, log_viewer),
    }

    content_area = ft.Column(expand=True, controls=[views["converter"]], spacing=0)

    def on_nav_change(e):
        idx = nav_rail.selected_index
        content_area.controls = [list(views.values())[idx]]
        page.update()

    def on_lang_change(e):
        lang = lang_dd.value
        settings.set("language", lang)
        set_language(lang)
        # Полная пересборка интерфейса на новом языке
        page.overlay.clear()
        page.controls.clear()
        main(page)

    # Переключатель языка (внизу бокового меню)
    lang_dd = ft.Dropdown(
        width=110,
        value=get_language(),
        options=[ft.dropdown.Option(code, name) for code, name in LANGUAGES.items()],
        on_change=on_lang_change,
        dense=True,
        text_size=12,
        border_radius=8,
    )

    nav_rail = ft.NavigationRail(
        selected_index=0,
        label_type=ft.NavigationRailLabelType.ALL,
        min_width=100,
        min_extended_width=200,
        destinations=[
            ft.NavigationRailDestination(icon=ft.Icons.SYNC_ALT, label=tr("nav_converter")),
            ft.NavigationRailDestination(icon=ft.Icons.MERGE_TYPE, label=tr("nav_merge")),
            ft.NavigationRailDestination(icon=ft.Icons.CLOUD_UPLOAD, label=tr("nav_import")),
        ],
        on_change=on_nav_change,
        trailing=ft.Container(
            content=lang_dd,
            padding=ft.padding.only(left=8, right=8, bottom=12),
        ),
    )

    page.add(
        ft.Row(
            [
                nav_rail,
                ft.VerticalDivider(width=1, thickness=1),
                ft.Column(
                    [
                        ft.Container(content=content_area, expand=True, padding=20),
                        log_viewer,
                    ],
                    expand=True,
                    spacing=0,
                ),
            ],
            expand=True,
            spacing=0,
        )
    )


if __name__ == "__main__":
    ft.app(target=main)
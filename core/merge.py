import json
import pathlib
from typing import Callable, Optional


def _messages_sort_key(path: pathlib.Path) -> int:
    """messages.json -> 1, messages2.json -> 2, messages10.json -> 10 (числовая сортировка!)."""
    suffix = path.stem[len("messages"):]
    return int(suffix) if suffix.isdigit() else 1


def merge_json_files(
    folder: pathlib.Path,
    log_callback: Optional[Callable[[str, str], None]] = None,
) -> bool:
    """
    Объединяет все messages*.json в один result.json.

    Args:
        folder: папка с JSON-файлами
        log_callback: функция логирования (message, level)
    """
    try:
        if log_callback:
            log_callback(f"Начало слияния JSON-файлов из: {folder}", "INFO")

        outfile = folder / "result.json"

        # Автоматический поиск файлов в правильном числовом порядке
        files = sorted(folder.glob("messages*.json"), key=_messages_sort_key)

        if not files:
            raise FileNotFoundError(f"Не найдено файлов messages*.json в {folder}")

        if log_callback:
            log_callback(f"Найдено файлов для слияния: {len(files)}", "INFO")

        all_messages = []
        meta = None

        for file in files:
            if not file.exists():
                if log_callback:
                    log_callback(f"⚠️ Пропущен файл: {file.name}", "WARNING")
                continue

            with open(file, encoding="utf-8") as f:
                data = json.load(f)

            # Поддержка обоих форматов (list или объект с ключом messages)
            if isinstance(data, dict) and "messages" in data:
                msgs = data["messages"]
                if meta is None:
                    meta = {k: v for k, v in data.items() if k != "messages"}
            elif isinstance(data, list):
                msgs = data
            else:
                if log_callback:
                    log_callback(f"⚠️ Неизвестный формат файла: {file.name}", "WARNING")
                continue

            all_messages.extend(msgs)
            if log_callback:
                log_callback(f"✅ Обработан: {file.name} ({len(msgs)} сообщений)", "SUCCESS")

        if meta is None:
            meta = {}

        result = meta.copy()
        result["messages"] = all_messages

        with open(outfile, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        if log_callback:
            log_callback(f"✅ Слияние завершено! Всего сообщений: {len(all_messages)}", "SUCCESS")
            log_callback(f"Итоговый файл: {outfile}", "INFO")

        return True

    except Exception as e:
        if log_callback:
            log_callback(f"❌ Ошибка слияния: {str(e)}", "ERROR")
        return False
import json
import math
import mimetypes
import os
import pathlib
import tempfile
from typing import Callable, Optional

from dateutil.parser import parse as parse_dt
from telethon import functions, types
from telethon.sync import TelegramClient


def _fmt_date(msg):
    try:
        dt = parse_dt(msg.get('date', ''))
        return dt.strftime('%d/%m/%y, %H:%M')
    except Exception:
        return ''


def _fmt_text(msg):
    ents = msg.get('text_entities') or []
    if isinstance(ents, list) and ents:
        return ''.join(e.get('text', '') for e in ents)
    return msg.get('text', '') or ''


def convert_json_to_whatsapp_format(data, only_n=math.inf):
    raw_msgs = data.get('messages', [])
    id_to_content = {}
    id_to_date = {}
    for m in raw_msgs:
        mid = m.get('id')
        id_to_date[mid] = _fmt_date(m)
        fp = m.get('file') or m.get('photo') or m.get('contact_vcard')
        if fp:
            id_to_content[mid] = pathlib.Path(fp).name
        else:
            id_to_content[mid] = _fmt_text(m)

    msgs = raw_msgs[:int(only_n)] if isinstance(only_n, (int, float)) and math.isfinite(only_n) else raw_msgs
    lines = []
    filelist = {}

    for msg in msgs:
        mtype = msg.get('type')
        if mtype == 'service':
            date_str = _fmt_date(msg)
            sender = msg.get('actor') or msg.get('from') or 'Unknown'
            prefix = f"{date_str} - {sender}: "
            action = msg.get('action', '')
            if action == 'pin_message':
                pid = msg.get('message_id')
                orig = id_to_content.get(pid, '')
                lines.append(f"{prefix}The message was pinned: '{orig}'\n")
            else:
                svc_map = {
                    'clear_history': 'History cleared',
                    'edit_chat_theme': f"The topic has been changed to {msg.get('emoticon', '')}",
                    'phone_call': f"Call ({msg.get('discard_reason', '')}, duration {msg.get('duration_seconds', 0)}s)"
                }
                text = svc_map.get(action, action)
                lines.append(f"{prefix}{text}\n")
            continue

        date_str = _fmt_date(msg)
        sender = msg.get('from') or msg.get('actor') or 'Unknown'
        prefix = f"{date_str} - {sender}: "

        if rid := msg.get('reply_to_message_id'):
            orig = id_to_content.get(rid, '')
            orig_time = id_to_date.get(rid, '')
            lines.append(f"{prefix}You replied to the message: '{orig}' ({orig_time})\n")
            reply = _fmt_text(msg)
            if reply:
                lines.append(f"{prefix}{reply}\n")
            continue

        if info := msg.get('contact_information'):
            text = f"Contact: {info.get('first_name', '')} {info.get('last_name', '')} {info.get('phone_number', '')}"
            lines.append(f"{prefix}{text}\n")
            continue

        if poll := msg.get('poll'):
            q = poll.get('question', '')
            opts = [ans['text'] for ans in poll.get('answers', [])]
            text = f"Poll: {q} [{', '.join(opts)}]"
            lines.append(f"{prefix}{text}\n")
            continue

        if loc := msg.get('location_information'):
            url = f"https://www.google.com/maps/search/?api=1&query={loc['latitude']},{loc['longitude']}"
            lines.append(f"{prefix}{url}\n")
            continue

        fp = msg.get('file') or msg.get('photo') or msg.get('contact_vcard')
        if fp and not (str(fp).startswith('http://') or str(fp).startswith('https://')):
            if fwd := msg.get('forwarded_from'):
                lines.append(f"{prefix}[Forwarded from {fwd}]\n")
            fn = pathlib.Path(fp).name
            attr = {'filename': fn, 'media_type': msg.get('media_type'), 'is_photo': bool(msg.get('photo'))}
            for a in ('duration_seconds', 'width', 'height', 'file_size', 'thumbnail', 'thumbnail_file_size'):
                if a in msg:
                    attr[a] = msg[a]
            filelist[fp] = attr
            lines.append(f"{prefix}{fn} (file attached)\n")
            caption = _fmt_text(msg)
            if caption:
                lines.append(f"{prefix}{caption}\n")
            continue

        parts = []
        if fwd := msg.get('forwarded_from'):
            parts.append(f"[Forwarded from {fwd}] ")
        parts.append(_fmt_text(msg))
        text = ''.join(parts).strip()
        if text:
            lines.append(f"{prefix}{text}\n")

    return lines, filelist


def upload_file(client, peer, imp_id, base_path, rel_path, info):
    path = base_path / rel_path
    fn = info['filename']
    mime = info.get('mime_type') or mimetypes.guess_type(fn)[0] or 'application/octet-stream'
    uf = client.upload_file(path)

    if info.get('media_type') == 'video_message':
        dur = info.get('duration_seconds', 0)
        w = info.get('width', 0)
        h = info.get('height', 0)
        attrs = [types.DocumentAttributeVideo(dur, w, h, round_message=True)]
        media = types.InputMediaUploadedDocument(file=uf, mime_type=mime, attributes=attrs)
    elif info.get('is_photo'):
        media = types.InputMediaUploadedPhoto(file=uf)
    else:
        attrs = [types.DocumentAttributeFilename(file_name=fn)]
        if 'width' in info and 'height' in info:
            attrs.append(types.DocumentAttributeImageSize(info['width'], info['height']))
        if info.get('media_type') == 'video_file' and 'duration_seconds' in info:
            attrs.append(types.DocumentAttributeVideo(info['duration_seconds'], info.get('width'), info.get('height')))
        if info.get('media_type') == 'animation':
            attrs.append(types.DocumentAttributeAnimated())
        if info.get('media_type') == 'sticker':
            attrs.append(types.DocumentAttributeSticker('', types.InputStickerSetEmpty()))
        if info.get('media_type') in ('audio_file', 'voice_message') and 'duration_seconds' in info:
            attrs.append(types.DocumentAttributeAudio(info['duration_seconds']))
        media = types.InputMediaUploadedDocument(file=uf, mime_type=mime, attributes=attrs)

    client(functions.messages.UploadImportedMediaRequest(
        peer=peer, import_id=imp_id, file_name=fn, media=media))


def import_history(
    path: pathlib.Path,
    peer_id: str,
    api_id: int,
    api_hash: str,
    auth_callback: Optional[Callable] = None,
    log_callback: Optional[Callable[[str, str], None]] = None,
    progress_callback: Optional[Callable[[float, str], None]] = None,
    test_only: bool = False,
    only_first_n: float = math.inf,
) -> bool:
    """
    Импорт истории чата в Telegram (адаптация import.py для GUI).
    """
    client = None
    try:
        json_file = path / 'result.json'
        if not json_file.exists():
            raise FileNotFoundError(f"Не найден result.json в {path}")

        if log_callback:
            log_callback("📖 Загрузка result.json...", "INFO")
        with open(json_file, encoding='utf-8') as f:
            data = json.load(f)

        if log_callback:
            log_callback("🔄 Конвертация в формат для импорта...", "INFO")
        messages, files = convert_json_to_whatsapp_format(data, only_first_n)
        head = ''.join(messages[:100])
        total_files = len(files)

        if log_callback:
            log_callback(f"✅ Подготовлено сообщений: {len(messages)}, медиа-файлов: {total_files}", "SUCCESS")
            log_callback("🔌 Инициализация Telethon-клиента...", "INFO")

        client = TelegramClient('telegram_import_gui', api_id, api_hash)
        client.connect()

        if not client.is_user_authorized():
            if auth_callback:
                if log_callback:
                    log_callback("🔐 Требуется авторизация...", "INFO")
                auth_callback(client)
            else:
                raise RuntimeError("Клиент не авторизован, а auth_callback не предоставлен.")

        if log_callback:
            log_callback(f"✅ Авторизация успешна. Поиск пира: {peer_id}...", "INFO")

        try:
            peer = client.get_entity(types.PeerChannel(int(peer_id)))
        except Exception:
            peer = peer_id

        if log_callback:
            log_callback("🛡️ Проверка возможности импорта...", "INFO")
        client(functions.messages.CheckHistoryImportRequest(import_head=head))
        client(functions.messages.CheckHistoryImportPeerRequest(peer=peer))

        if log_callback:
            log_callback("📤 Загрузка текстового дампа истории...", "INFO")
        tmp = tempfile.NamedTemporaryFile('w+t', delete=False, encoding='utf-8',
                                          prefix='imp_', suffix='.txt')
        tmp.writelines(messages)
        tmp.close()
        up = client.upload_file(tmp.name)
        history = client(functions.messages.InitHistoryImportRequest(
            peer=peer, file=up, media_count=total_files))
        os.remove(tmp.name)

        if log_callback:
            log_callback("📦 Загрузка медиа-файлов...", "INFO")

        files_items = list(files.items())
        for idx, (rel, info) in enumerate(files_items):
            if progress_callback:
                progress_callback((idx + 1) / max(total_files, 1), info['filename'])
            if log_callback:
                log_callback(f"⬆️ [{idx + 1}/{total_files}] {info['filename']}", "INFO")
            try:
                upload_file(client, peer, history.id, path, rel, info)
            except Exception as e:
                if log_callback:
                    log_callback(f"❌ Ошибка загрузки {info['filename']}: {str(e)}", "ERROR")
                continue

        if test_only:
            if log_callback:
                log_callback("🏁 Тестовый режим завершён. Финальный импорт не выполнен.", "INFO")
            return True

        if log_callback:
            log_callback("🚀 Запуск финального импорта истории...", "INFO")
        client(functions.messages.StartHistoryImportRequest(peer=peer, import_id=history.id))

        if log_callback:
            log_callback("🎉 Импорт истории успешно завершён!", "SUCCESS")
        return True

    except Exception as e:
        if log_callback:
            log_callback(f"❌ Критическая ошибка импорта: {str(e)}", "ERROR")
        return False
    finally:
        if client is not None:
            try:
                client.disconnect()
            except Exception:
                pass
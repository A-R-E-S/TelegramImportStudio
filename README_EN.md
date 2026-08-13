[🇷🇺 Russian](README.md) • [🇬🇧 English](README_EN.md)

<div align="center">

# 📨 Telegram Import Studio

**HTML → JSON → Telegram**

A desktop application for restoring and importing Telegram Desktop chat history:
converts an HTML backup to JSON, merges parts, and imports the history
into Telegram via Telethon.

<br>

[![Stars](https://img.shields.io/github/stars/A-R-E-S/TelegramImportStudio?style=social)](https://github.com/A-R-E-S/TelegramImportStudio/stargazers)
[![Forks](https://img.shields.io/github/forks/A-R-E-S/TelegramImportStudio?style=social)](https://github.com/A-R-E-S/TelegramImportStudio/network/members)
[![Views](https://komarev.com/ghp/?username=A-R-E-S&color=blueviolet&label=Views)](https://github.com/A-R-E-S)

[![Release](https://img.shields.io/github/v/release/A-R-E-S/TelegramImportStudio?include_prereleases&label=Release&logo=github&style=flat-square)](https://github.com/A-R-E-S/TelegramImportStudio/releases)
[![Downloads](https://img.shields.io/github/downloads/A-R-E-S/TelegramImportStudio/total?label=Downloads&logo=github&style=flat-square&color=2ea44f)](https://github.com/A-R-E-S/TelegramImportStudio/releases)
[![VirusTotal](https://img.shields.io/badge/VirusTotal-Report-3975ff?style=flat-square&logo=virustotal&logoColor=white)](https://www.virustotal.com/gui/file/399958769a517c1bf079cce78270f1d7bc42aad9249a482e173b84f16893db32?nocache=1)
[![Python](https://img.shields.io/badge/Python-3.10+-blue?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![Flet](https://img.shields.io/badge/Flet-0.25+-7c4dff?style=flat-square&logo=flutter&logoColor=white)](https://flet.dev/)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)

</div>

---

## 🎬 What the imported history looks like

<p align="center">
  <img src="assets/demo.gif" width="410" alt="Imported messages in Telegram"/>
</p>

---

## 📥 Download

<p align="center">
  <a href="https://github.com/A-R-E-S/TelegramImportStudio/releases/latest">
    <img src="https://img.shields.io/badge/⬇_DOWNLOAD_FOR_WINDOWS-2ea44f?style=for-the-badge&logo=windows&logoColor=white" alt="Download for Windows"/>
  </a>
</p>

<p align="center">
  Or run from source — <a href="#-run-from-source">instructions below</a>.
</p>

---

## ✨ Features

- 📦 Convert Telegram Desktop HTML export to JSON
- 🔗 Merge `messages.json`, `messages2.json`, … into a single `result.json`
- 📤 Import history into Telegram via Telethon
  (CheckHistoryImport → Init → UploadMedia → Start)
- 🖼️ Support for all content types:
  formatted text, photos, videos, video messages ("circles"), voice messages, stickers
  (`.webp` / `.tgs` / `.webm`), GIFs, documents, locations, polls,
  contacts, calls, pinned messages, forwarded messages, replies
- 🌍 Interface: **RU / EN / ES / DE / FR**
- 🔐 Login via Telegram/SMS code and 2FA password directly in the GUI
- 🧪 Test mode and importing only the first N messages
- 👥 Sender map (sender_map): names from the backup → real user_ids
- 📊 Progress bars and built-in execution console

---

## 📸 Screenshots

| 📦 Converter | 🔗 Merge | 📤 Import |
|:---:|:---:|:---:|
| <img src="assets/screenshot-converter.png" width="260"/> | <img src="assets/screenshot-merge.png" width="260"/> | <img src="assets/screenshot-import.png" width="260"/> |

---

🛡️ Security

    The application runs entirely locally: backups, API data, and sessions
    are not sent anywhere except Telegram servers.
    The release is scanned on VirusTotal — the report is linked in the badge at the top of the page.

## 🚀 Run from Source

### Requirements

- Windows 10/11 x64
- Python 3.10+

### Steps

```bash
git clone https://github.com/A-R-E-S/TelegramImportStudio.git
cd TelegramImportStudio

python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux / macOS:
# source .venv/bin/activate

pip install -r requirements.txt
python main.py
```

## 🔑 How to get API ID and API Hash

1. Go to [my.telegram.org](https://my.telegram.org).
2. Log in using your phone number.
3. Open the **API development tools** section.
4. Copy the `api_id` and `api_hash` into the corresponding fields on the "Import" screen in the app.

> 💡 The data is stored locally in the `settings.json` file and is not sent anywhere.

## ❓ Frequently Asked Questions

**Where to get the Chat ID?**  
Via the [@userinfobot](https://t.me/userinfobot) or [@getidsbot](https://t.me/getidsbot) bot in Telegram.

**Where to get the user_id for the sender_map?**  
Via the [@userinfobot](https://t.me/userinfobot) bot.

**Why does the antivirus flag the .exe?**  
This is a false positive due to PyInstaller packaging. Verify the SHA256 and check the VirusTotal report above.

**What does the test mode do?**  
It goes through the entire process (preparation, authorization, media upload) but does not launch the final history import.

**What happens if the internet connection drops during the import?**  
Some files might fail to upload — they will be marked as errors in the console. You can restart the import: the skipped messages will be sent again.

**Where is the Telegram session stored?**  
In the `telegram_import_gui.session` file next to the running `.exe` (or next to `main.py` if running from source).

## ⚠️ Disclaimer

The project is intended to work **with your own data and your own accounts**.

The author is not responsible for violating Telegram's terms of service, account bans, data loss, or misuse of the API. By using the program, you accept all risks.

## 📄 License

The project is distributed under the [MIT](LICENSE) license.

---

<div align="center">

### If you found this project helpful — give it a ⭐
It really helps the project's development!

</div>

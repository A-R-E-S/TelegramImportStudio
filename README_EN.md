[🇬🇧 English](README_EN.md)

<div align="center">

# 📨 Telegram Import Studio

**HTML → JSON → Telegram**

A desktop app that restores and imports Telegram Desktop chat history:
converts an HTML backup to JSON, merges the parts and imports
the history into Telegram via Telethon.

<br>

[![Stars](https://img.shields.io/github/stars/A-R-E-S/telegram-import-gui?style=social)](https://github.com/A-R-E-S/telegram-import-gui/stargazers)
[![Forks](https://img.shields.io/github/forks/A-R-E-S/telegram-import-gui?style=social)](https://github.com/A-R-E-S/telegram-import-gui/network/members)
[![Views](https://komarev.com/ghp/?username=A-R-E-S&color=blueviolet&label=Views)](https://github.com/A-R-E-S)

[![Release](https://img.shields.io/github/v/release/A-R-E-S/telegram-import-gui?include_prereleases&label=Release&logo=github&style=flat-square)](https://github.com/A-R-E-S/telegram-import-gui/releases)
[![Downloads](https://img.shields.io/github/downloads/A-R-E-S/telegram-import-gui/total?label=Downloads&logo=github&style=flat-square&color=2ea44f)](https://github.com/A-R-E-S/telegram-import-gui/releases)
[![VirusTotal](https://img.shields.io/badge/VirusTotal-Report-3975ff?style=flat-square&logo=virustotal&logoColor=white)](VT_REPORT_URL)
[![Python](https://img.shields.io/badge/Python-3.10+-blue?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![Flet](https://img.shields.io/badge/Flet-0.25+-7c4dff?style=flat-square&logo=flutter&logoColor=white)](https://flet.dev/)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)

</div>

---

## 🎬 Imported history preview

<p align="center">
  <img src="assets/demo.gif" width="820" alt="Imported messages in Telegram"/>
</p>

---

## 📥 Download

<p align="center">
  <a href="https://github.com/A-R-E-S/telegram-import-gui/releases/latest">
    <img src="https://img.shields.io/badge/⬇_DOWNLOAD_FOR_WINDOWS-2ea44f?style=for-the-badge&logo=windows&logoColor=white" alt="Download for Windows"/>
  </a>
</p>

<p align="center">
  Or run from source — <a href="#-run-from-source">see below</a>.
</p>

---

## ✨ Features

- 📦 Converts Telegram Desktop HTML exports to JSON
- 🔗 Merges `messages.json`, `messages2.json`, … into a single `result.json`
- 📤 Imports history into Telegram via Telethon
- 🖼️ Photos, videos, round videos, voice notes, stickers, documents, locations, polls, calls, pins, forwards
- 🌍 UI languages: RU / EN / ES / DE / FR
- 🔐 Login code (Telegram/SMS) and 2FA password via GUI dialogs
- 🧪 Test mode and “first N messages only” import
- 📊 Progress bars and a built-in execution console

---

## 📸 Screenshots

| 📦 Converter | 🔗 Merge | 📤 Import |
|:---:|:---:|:---:|
| <img src="assets/screenshot-converter.png" width="260"/> | <img src="assets/screenshot-merge.png" width="260"/> | <img src="assets/screenshot-import.png" width="260"/> |

---

## 🔄 How it works

```mermaid
graph LR
    A[Telegram Desktop<br/>HTML export] --> B[📦 Converter]
    B --> C[messages*.json]
    C --> D[🔗 Merge]
    D --> E[result.json]
    E --> F[📤 Import<br/>Telethon]
    F --> G[💬 History in Telegram]
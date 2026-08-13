[🇷🇺 Русский](README.md) • [🇬🇧 English](README_EN.md)

<div align="center">

# 📨 Telegram Import Studio

**HTML → JSON → Telegram**

Десктопное приложение для восстановления и импорта истории чатов Telegram Desktop:
конвертирует HTML-бэкап в JSON, объединяет части и импортирует историю
в Telegram через Telethon.

<br>

[![Stars](https://img.shields.io/github/stars/A-R-E-S/telegram-import-gui?style=social)](https://github.com/A-R-E-S/telegram-import-gui/stargazers)
[![Forks](https://img.shields.io/github/forks/A-R-E-S/telegram-import-gui?style=social)](https://github.com/A-R-E-S/telegram-import-gui/network/members)
[![Views](https://komarev.com/ghp/?username=A-R-E-S&color=blueviolet&label=Views)](https://github.com/A-R-E-S)

[![Release](https://img.shields.io/github/v/release/A-R-E-S/telegram-import-gui?include_prereleases&label=Release&logo=github&style=flat-square)](https://github.com/A-R-E-S/telegram-import-gui/releases)
[![Downloads](https://img.shields.io/github/downloads/A-R-E-S/telegram-import-gui/total?label=Downloads&logo=github&style=flat-square&color=2ea44f)](https://github.com/A-R-E-S/telegram-import-gui/releases)
[![VirusTotal](https://img.shields.io/badge/VirusTotal-Отчёт-3975ff?style=flat-square&logo=virustotal&logoColor=white)](VT_REPORT_URL)
[![Python](https://img.shields.io/badge/Python-3.10+-blue?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![Flet](https://img.shields.io/badge/Flet-0.25+-7c4dff?style=flat-square&logo=flutter&logoColor=white)](https://flet.dev/)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)

</div>

---

## 🎬 Как выглядит импортированная история

<p align="center">
  <img src="assets/demo.gif" width="820" alt="Импортированные сообщения в Telegram"/>
</p>

---

## 📥 Скачать

<p align="center">
  <a href="https://github.com/A-R-E-S/telegram-import-gui/releases/latest">
    <img src="https://img.shields.io/badge/⬇_СКАЧАТЬ_ДЛЯ_WINDOWS-2ea44f?style=for-the-badge&logo=windows&logoColor=white" alt="Скачать для Windows"/>
  </a>
</p>

<p align="center">
  Или запусти из исходников — <a href="#-запуск-из-исходников">инструкция ниже</a>.
</p>

---

## ✨ Возможности

- 📦 Конвертация HTML-экспорта Telegram Desktop в JSON
- 🔗 Слияние `messages.json`, `messages2.json`, … в один `result.json`
- 📤 Импорт истории в Telegram через Telethon
- 🖼️ Фото, видео, кружки, голосовые, стикеры, документы, геолокация, опросы, звонки, пины, форварды
- 🌍 Интерфейс: RU / EN / ES / DE / FR
- 🔐 Вход по коду из Telegram/SMS и паролю 2FA прямо в GUI
- 🧪 Тестовый режим и импорт только первых N сообщений
- 📊 Прогресс-бары и встроенная консоль выполнения

---

## 📸 Скриншоты

| 📦 Конвертер | 🔗 Слияние | 📤 Импорт |
|:---:|:---:|:---:|
| <img src="assets/screenshot-converter.png" width="260"/> | <img src="assets/screenshot-merge.png" width="260"/> | <img src="assets/screenshot-import.png" width="260"/> |

---

## 🔄 Как это работает

```mermaid
graph LR
    A[Telegram Desktop<br/>HTML-экспорт] --> B[📦 Конвертер]
    B --> C[messages*.json]
    C --> D[🔗 Слияние]
    D --> E[result.json]
    E --> F[📤 Импорт<br/>Telethon]
    F --> G[💬 История в Telegram]
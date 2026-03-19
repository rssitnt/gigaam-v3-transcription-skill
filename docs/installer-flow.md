# Установщик верхнего уровня

Этот слой нужен для сценария «скачал репозиторий и запустил один installer».

## Windows

Главный вход:

`C:\projects\automations\gigaam-v3-transcription-skill\scripts\install.ps1`

Что он делает:
- проверяет наличие `python` / `py`;
- если Python не найден, пытается поставить его через `winget`;
- после этого запускает bootstrap skill runtime;
- bootstrap уже сам разбирается с `ffmpeg`, GigaAM, venv и config.

Запуск:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\install.ps1
```

## Linux

Главный вход:

`C:\projects\automations\gigaam-v3-transcription-skill\scripts\install.sh`

Что он делает:
- проверяет наличие `python3` / `python`;
- если Python не найден, пытается поставить его через `apt-get`, `dnf` или `pacman`;
- затем запускает bootstrap skill runtime.

Запуск:

```bash
bash ./scripts/install.sh
```

## Честные ограничения

- На Linux автоустановка Python использует `sudo` и системный пакетный менеджер.
- На Windows автоустановка Python требует доступный `winget`.
- Это максимально близко к «всё ставится само», но всё ещё зависит от прав машины и наличия системных инструментов установки.

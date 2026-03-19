# INSTALL

Если ты агент и тебе дали ссылку на этот репозиторий со словами **«скачай skill»**, делай только это.

## Windows

1. Клонируй репозиторий.
2. Запусти:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\install-from-url.ps1 -RepoUrl https://github.com/rssitnt/gigaam-v3-transcription-skill.git
```

## Linux

1. Клонируй репозиторий.
2. Запусти:

```bash
bash ./scripts/install-from-url.sh https://github.com/rssitnt/gigaam-v3-transcription-skill.git
```

## После установки

Источник истины для результата:

`C:\projects\automations\gigaam-v3-transcription-skill\artifacts\install-report.json`

Считай установку успешной, если в report стоит:

- `ready: true`

## Что сообщить пользователю в конце

Коротко скажи:
- skill установлен или нет;
- где лежит репозиторий;
- где лежит config;
- какой командой запускать транскрибацию.

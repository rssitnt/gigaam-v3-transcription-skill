# INSTALL

Если ты агент и пользователь сказал **«скачай skill»**, делай только это.

## Windows

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\install-from-url.ps1 -RepoUrl https://github.com/rssitnt/gigaam-v3-transcription-skill.git
```

## Linux

```bash
bash ./scripts/install-from-url.sh https://github.com/rssitnt/gigaam-v3-transcription-skill.git
```

## Критерий успеха

Установка успешна, если в файле

`C:\projects\automations\gigaam-v3-transcription-skill\artifacts\install-report.json`

стоит:

- `ready: true`

## Что сказать пользователю

Коротко сообщи:
- установлен ли skill;
- где лежит репозиторий;
- какой `env_id` активен;
- где лежит config;
- какой командой запускать транскрибацию.

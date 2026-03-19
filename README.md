# gigaam-v3-transcription-skill

<p align="center">
  <img src="docs/images/skill-creator-banner.jpg" alt="GigaAM-v3 transcription skill" width="1200">
</p>

Skill для локальной транскрибации через **GigaAM-v3**.

## Если ты агент

Открой:

`C:\projects\automations\gigaam-v3-transcription-skill\INSTALL.md`

## Что делает

- транскрибирует аудио;
- транскрибирует голосовые сообщения;
- транскрибирует звук из видео;
- пишет:
  - `transcript.txt`
  - `transcript.json`
  - `final_summary.json`

## Самый короткий install path

### Windows

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\install-from-url.ps1 -RepoUrl https://github.com/rssitnt/gigaam-v3-transcription-skill.git
```

### Linux

```bash
bash ./scripts/install-from-url.sh https://github.com/rssitnt/gigaam-v3-transcription-skill.git
```

## Критерий успеха

Проверить файл:

`C:\projects\automations\gigaam-v3-transcription-skill\artifacts\install-report.json`

Установка успешна, если там стоит:

- `ready: true`

## Главное в репозитории

- install entry: `C:\projects\automations\gigaam-v3-transcription-skill\INSTALL.md`
- machine-readable manifest: `C:\projects\automations\gigaam-v3-transcription-skill\install-manifest.json`
- skill: `C:\projects\automations\gigaam-v3-transcription-skill\skill`
- packaged artifact: `C:\projects\automations\gigaam-v3-transcription-skill\artifacts\skill.skill`

## Честно

- первый bootstrap может быть долгим;
- runtime поднимается локально;
- Python/ffmpeg/bootstrap максимально автоматизированы, но всё ещё зависят от прав и системных инструментов машины.

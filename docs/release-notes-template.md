# Шаблон release notes

## gigaam-v3-transcription-skill v0.1.0

### Что входит в релиз

- публичный AgentSkill для локальной транскрибации через GigaAM-v3
- bootstrap-скрипт для project-local runtime
- standalone runtime adapter
- wrapper для транскрибации локального медиафайла
- packaged skill artifact

### Что создаёт skill

- `transcript.txt`
- `transcript.json`
- `final_summary.json`

### Что требуется

- Python 3
- `ffmpeg` или возможность автодотягивания `ffmpeg` через bootstrap
- сеть на первом bootstrap

### Честные ограничения

- первый запуск может занимать время, потому что нужно подготовить зависимости и модель;
- перед первой реальной транскрибацией нужно поднять локальный runtime;
- базовый публичный контур уже готов, но следующие релизы ещё могут улучшить UX и тестовое покрытие.

### Основные пути

- репозиторий: `C:\projects\automations\gigaam-v3-transcription-skill`
- skill: `C:\projects\automations\gigaam-v3-transcription-skill\skill`
- packaged artifact: `C:\projects\automations\gigaam-v3-transcription-skill\artifacts\skill.skill`

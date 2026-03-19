---
name: gigaam-v3-transcription
description: Локальная транскрибация аудио, голосовых сообщений, звука из видео и извлечённого YouTube-аудио через GigaAM-v3. Используй, когда агенту нужен локальный ASR-контур для медиафайлов и нужны артефакты транскрибации на диске.
---

# GigaAM-v3 transcription

Используй этот skill, чтобы транскрибировать локальный медиафайл через локальный runtime GigaAM-v3.

## Быстрый старт

1. Убедись, что медиафайл лежит локально и путь к нему абсолютный.
2. Если runtime ещё не подготовлен, прочитай:
   - `{baseDir}/references/setup.md`
3. Запусти:
   - `python3 {baseDir}/scripts/run_gigaam_transcription.py --input /absolute/path/to/file --env-file {baseDir}/config/local.env`
4. Используй возвращённые пути к артефактам как источник истины.

## Для чего использовать этот skill

- локальная транскрибация аудио;
- транскрибация голосовых сообщений;
- транскрибация звука из видео;
- fallback-транскрибация, когда публичные captions не отдали текст.

## Workflow

### 1. Проверить вход

Требуй локальный абсолютный путь.

### 2. Если нужно — сделать bootstrap

Если `config/local.env` отсутствует или `GIGAAM_LOCAL_PYTHON` пустой, прочитай:
- `{baseDir}/references/setup.md`

### 3. Запустить wrapper

```bash
python3 {baseDir}/scripts/run_gigaam_transcription.py --input /absolute/path/to/file --env-file {baseDir}/config/local.env
```

Полезные флаги:
- `--title`
- `--language-hint`
- `--kind`
- `--output-dir`
- `--env-file`

### 4. Доверять артефактам, а не чату

Используй эти файлы:
- `transcript.txt`
- `transcript.json`
- `final_summary.json`

### 5. Сообщать честно

Если runtime/config/bootstrap не готовы, сообщи точный блокер и укажи на setup.

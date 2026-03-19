# Настройка

## Публичный bootstrap path

1. Запусти bootstrap:

```bash
python3 {baseDir}/scripts/bootstrap_gigaam_runtime.py
```

Что он подготавливает:
- локальный клон GigaAM в repo-level `.runtime/GigaAM`
- локальный venv в repo-level `.runtime/gigaam-venv`
- config-файл в `skill/config/local.env`
- путь к `ffmpeg` в одном из трёх режимов:
  - взять из system PATH;
  - упасть, если выбран `--ffmpeg-mode system`, а `ffmpeg` не найден;
  - автоматически скачать portable/static build, если это нужно

## Первый smoke-run

```bash
python3 {baseDir}/scripts/run_gigaam_transcription.py \
  --input /absolute/path/to/file \
  --env-file {baseDir}/config/local.env
```

## Честные ограничения

- bootstrap использует сеть для clone/install зависимостей;
- если `ffmpeg` нет в PATH, bootstrap может скачать portable/static build в runtime-область репозитория;
- на первом запуске подготовка модели и кеша может занять время.

# AGENT.md

Ты работаешь над проектом:

`C:\projects\automations\gigaam-v3-transcription-skill`

## Миссия

Собрать **публичный standalone skill** для агентов, который даёт локальную транскрибацию через GigaAM-v3.

## Главное правило

Это **не внутренний локальный хак** и не skill под конкретную машину qwert.
Это должен быть **GitHub-ready проект**, который другой человек сможет скачать и довести до рабочего состояния по инструкции.

## Что нельзя делать

- не хардкодить пути вида `/home/qwert/...`
- не завязывать skill на текущий workspace OpenClaw
- не ссылаться на внутренние приватные проекты как на обязательную зависимость
- не делать вид, что всё готово, если runtime bootstrap не автономен

## Что нужно сделать

1. Держать skill в папке:
   `C:\projects\automations\gigaam-v3-transcription-skill\skill`
2. Сделать wrapper-script для транскрибации локального файла.
3. Сделать bootstrap/setup path для локального GigaAM-v3 runtime.
4. Вынести конфиг в env/config, а не в код.
5. Подготовить packaging path для `.skill`.
6. Подготовить smoke-test path.
7. Описать честные ограничения.

## Целевой UX

Пользователь должен пройти примерно такой путь:

1. скачал репозиторий;
2. создал env/config;
3. запустил bootstrap;
4. упаковал skill;
5. использовал skill для транскрибации локального media file.

## Expected deliverables

- рабочий `skill/SKILL.md`
- `skill/scripts/*.py`
- setup/bootstrap instruction
- example config
- tests/smoke test
- packaged `.skill`

## Truth rules

Если какой-то шаг ещё не готов, фиксируй это честно в документации и не маскируй как finished.

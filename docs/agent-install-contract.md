# Agent-first install contract

Цель: дать даже простому агенту достаточно структуры, чтобы он смог установить skill по одной ссылке.

## Источники истины для агента

- короткая инструкция: `C:\projects\automations\gigaam-v3-transcription-skill\INSTALL.md`
- machine-readable manifest: `C:\projects\automations\gigaam-v3-transcription-skill\install-manifest.json`

## Минимальный сценарий для агента

1. Получить URL репозитория.
2. Запустить URL-first installer:
   - Windows: `scripts/install-from-url.ps1`
   - Linux: `scripts/install-from-url.sh`
3. Дождаться verify:
   - `scripts/verify_install.py`
4. Прочитать `artifacts/install-report.json`.
5. Сообщить человеку только короткий итог:
   - установлен ли skill;
   - где лежит repo;
   - где лежит config;
   - чем запускать транскрибацию.

## URL-first path

### Windows

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\install-from-url.ps1 -RepoUrl <repo-url>
```

### Linux

```bash
bash ./scripts/install-from-url.sh <repo-url>
```

## Критерий успеха

Установка считается успешной, если `scripts/verify_install.py` возвращает `ready: true` и пишет `artifacts/install-report.json`.

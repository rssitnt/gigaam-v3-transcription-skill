# Инструкция по публикации

Используй эту инструкцию, когда репозиторий готов к отправке на GitHub.

## Путь к репозиторию

`C:\projects\automations\gigaam-v3-transcription-skill`

## 1. Финальная проверка перед публикацией

Запусти:

```bash
cd /mnt/c/projects/automations/gigaam-v3-transcription-skill
git status --short
```

Ожидаемый результат:
- нет неожиданных tracked-изменений;
- в diff нет секретов;
- в staged-файлах нет runtime/cache-мусора.

## 2. Проверить упаковку

Запусти:

```bash
python3 /home/qwert/.npm-global/lib/node_modules/openclaw/skills/skill-creator/scripts/package_skill.py \
  /mnt/c/projects/automations/gigaam-v3-transcription-skill/skill \
  /mnt/c/projects/automations/gigaam-v3-transcription-skill/artifacts
```

Ожидаемый артефакт:
- `C:\projects\automations\gigaam-v3-transcription-skill\artifacts\skill.skill`

## 3. Проверить, что bootstrap-инструкции всё ещё честные

Проверь:
- `C:\projects\automations\gigaam-v3-transcription-skill\README.md`
- `C:\projects\automations\gigaam-v3-transcription-skill\skill\references\setup.md`
- `C:\projects\automations\gigaam-v3-transcription-skill\docs\release-checklist.md`

## 4. Создать GitHub-репозиторий

Пример:
- имя репозитория: `gigaam-v3-transcription-skill`
- видимость: выбрать осознанно — public или private

## 5. Запушить репозиторий

Пример:

```bash
cd /mnt/c/projects/automations/gigaam-v3-transcription-skill
git remote add origin <github-repo-url>
git push -u origin master
```

Если используешь `main`, сначала переименуй ветку:

```bash
git branch -M main
git push -u origin main
```

## 6. Дополнительный релизный артефакт

Можно прикрепить к GitHub Release:
- `C:\projects\automations\gigaam-v3-transcription-skill\artifacts\skill.skill`

## 7. Что писать в первом релизе

Рекомендуемый смысл первого релиза:
- локальный skill транскрибации на GigaAM-v3;
- project-local bootstrap flow;
- packaged `.skill`;
- артефакты транскрибации: txt/json/summary;
- честные требования к runtime: Python, ffmpeg, first-run downloads.

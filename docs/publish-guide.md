# Publish guide

Use this guide when the repository is ready to be pushed to GitHub.

## Repository path

`C:\projects\automations\gigaam-v3-transcription-skill`

## 1. Final pre-publish check

Run:

```bash
cd /mnt/c/projects/automations/gigaam-v3-transcription-skill
git status --short
```

Expected result:
- no unexpected tracked changes
- no secrets in diff
- no runtime/cache noise in staged files

## 2. Validate packaging

Run:

```bash
python3 /home/qwert/.npm-global/lib/node_modules/openclaw/skills/skill-creator/scripts/package_skill.py \
  /mnt/c/projects/automations/gigaam-v3-transcription-skill/skill \
  /mnt/c/projects/automations/gigaam-v3-transcription-skill/artifacts
```

Expected artifact:
- `C:\projects\automations\gigaam-v3-transcription-skill\artifacts\skill.skill`

## 3. Verify bootstrap instructions are still honest

Check:
- `C:\projects\automations\gigaam-v3-transcription-skill\README.md`
- `C:\projects\automations\gigaam-v3-transcription-skill\skill\references\setup.md`
- `C:\projects\automations\gigaam-v3-transcription-skill\docs\release-checklist.md`

## 4. Create GitHub repository

Example:
- repo name: `gigaam-v3-transcription-skill`
- visibility: choose public or private intentionally

## 5. Push repository

Example:

```bash
cd /mnt/c/projects/automations/gigaam-v3-transcription-skill
git remote add origin <github-repo-url>
git push -u origin master
```

If using `main`, rename branch first:

```bash
git branch -M main
git push -u origin main
```

## 6. Optional release asset

You can attach this file to a GitHub Release:
- `C:\projects\automations\gigaam-v3-transcription-skill\artifacts\skill.skill`

## 7. Recommended first release text

Recommended first release message:
- local GigaAM-v3 transcription skill
- project-local bootstrap flow
- packaged `.skill`
- transcript artifacts: txt/json/summary
- honest runtime prerequisites: Python, ffmpeg, first-run downloads

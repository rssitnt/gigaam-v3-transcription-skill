# Release checklist

Use this before publishing the repo publicly.

## Repository quality

- [ ] README matches the current repo behavior
- [ ] no private machine-only paths remain in required runtime logic
- [ ] `.gitignore` excludes runtime/cache/local smoke artifacts
- [ ] no secrets are committed
- [ ] packaged skill can be rebuilt from repo contents

## Runtime quality

- [ ] bootstrap works on a clean machine
- [ ] `ffmpeg` prerequisite is documented clearly
- [ ] config file generation is documented clearly
- [ ] smoke transcription succeeds on a local fixture

## Skill quality

- [ ] `skill/SKILL.md` matches the actual scripts
- [ ] references are minimal and useful
- [ ] packaged `.skill` validates successfully
- [ ] wrapper writes `transcript.txt`, `transcript.json`, `final_summary.json`

## Release outputs

- [ ] create/update GitHub repo
- [ ] push clean commit history
- [ ] attach `artifacts/skill.skill` to release if needed
- [ ] include quick-start commands in release notes

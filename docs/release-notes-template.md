# Release notes template

## gigaam-v3-transcription-skill v0.1.0

### What is included

- public AgentSkill for local GigaAM-v3 transcription
- bootstrap script for project-local runtime setup
- standalone runtime adapter
- wrapper script for local media transcription
- packaged skill artifact

### What the skill produces

- `transcript.txt`
- `transcript.json`
- `final_summary.json`

### Requirements

- Python 3
- `ffmpeg`
- network access on first bootstrap

### Honest limitations

- first run can take time because dependencies/models must be prepared
- local runtime setup is required before first real transcription
- public distribution baseline is ready, but future releases can still improve test coverage and UX polish

### Main paths

- repo: `C:\projects\automations\gigaam-v3-transcription-skill`
- skill: `C:\projects\automations\gigaam-v3-transcription-skill\skill`
- packaged artifact: `C:\projects\automations\gigaam-v3-transcription-skill\artifacts\skill.skill`

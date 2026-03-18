# Public skill spec

## Product

Public AgentSkill: `gigaam-v3-transcription`

## Purpose

Provide a local-first transcription skill for:
- audio
- voice notes
- video-audio
- extracted YouTube audio

## Expected user value

The user installs one skill and gets a repeatable local ASR path based on GigaAM-v3.

## Public distribution constraints

- repository must be self-contained
- setup flow must be documented
- skill must not depend on hidden local repos
- configuration must be externalized
- packaged `.skill` must be buildable from this repo

## Minimum public capabilities

1. accept a local absolute media path
2. run GigaAM-v3 on that file
3. write:
   - transcript.txt
   - transcript.json
   - final_summary.json
4. return artifact paths
5. fail with clear actionable error if runtime/config is missing

## Nice-to-have later

- language hints
- chunk controls
- output directory override
- YouTube audio fallback helper
- transcript summarization helper

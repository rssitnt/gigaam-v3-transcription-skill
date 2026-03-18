#!/usr/bin/env python3
import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import wave
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

DEFAULT_MODEL = "v3_e2e_rnnt"
DEFAULT_CHUNK_SECONDS = 22.0
AUDIO_SUFFIXES = {".aac", ".flac", ".m4a", ".mp3", ".ogg", ".opus", ".wav", ".weba"}
VIDEO_SUFFIXES = {".avi", ".m4v", ".mkv", ".mov", ".mp4", ".mpeg", ".mpg", ".webm"}


def _collapse(value: Any) -> str:
    return " ".join(str(value or "").strip().split())


def _iso_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _json_dump(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while True:
            chunk = handle.read(1024 * 1024)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def _resolve_ffmpeg(explicit: Optional[str]) -> Optional[str]:
    candidate = _collapse(explicit) or _collapse(os.environ.get("GIGAAM_FFMPEG_BIN"))
    if candidate:
        if os.path.isabs(candidate):
            return candidate if Path(candidate).exists() else None
        return shutil.which(candidate)
    return shutil.which("ffmpeg")


def _allow_network(explicit: bool) -> bool:
    if explicit:
        return True
    return _collapse(os.environ.get("GIGAAM_ALLOW_NETWORK")).lower() in {"1", "true", "yes", "on"}


def _runtime_probe_payload(*, model_name: str, ffmpeg_path: Optional[str], allow_network: bool) -> Dict[str, Any]:
    payload: Dict[str, Any] = {
        "generated_at": _iso_now(),
        "engine": "public-gigaam-skill-runtime",
        "model": model_name,
        "python_executable": sys.executable,
        "python_version": sys.version.split()[0],
        "ffmpeg_path": ffmpeg_path,
        "ffmpeg_available": bool(ffmpeg_path),
        "allow_network_model_download": allow_network,
        "gigaam_importable": False,
        "model_loadable": False,
        "chunking_strategy": f"fixed-window-{DEFAULT_CHUNK_SECONDS:.0f}s",
        "ready": False,
        "blocker": None,
        "safe_next_step": None,
    }
    try:
        if not allow_network:
            os.environ.setdefault("HF_HUB_OFFLINE", "1")
            os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
        import gigaam  # type: ignore

        payload["gigaam_importable"] = True
        gigaam.load_model(model_name)
        payload["model_loadable"] = True
    except Exception as exc:
        payload["blocker"] = _collapse(exc)
    if not payload["ffmpeg_available"]:
        payload["blocker"] = payload["blocker"] or "ffmpeg is not installed or not reachable in PATH."
    payload["ready"] = bool(payload["ffmpeg_available"] and payload["gigaam_importable"] and payload["model_loadable"])
    payload["safe_next_step"] = (
        "Run run_gigaam_transcription.py on one local file."
        if payload["ready"]
        else "Run bootstrap_gigaam_runtime.py, ensure ffmpeg is installed, then rerun probe."
    )
    return payload


def _stringify_transcription(raw: Any) -> str:
    if isinstance(raw, str):
        return _collapse(raw)
    if isinstance(raw, dict):
        return _collapse(raw.get("text") or raw.get("transcription"))
    return _collapse(raw)


def _normalize_audio(*, input_path: Path, kind: str, ffmpeg_path: Optional[str], temp_dir: Path) -> Dict[str, Any]:
    suffix = input_path.suffix.lower()
    if suffix == ".wav":
        return {
            "audio_path": input_path,
            "used_ffmpeg": False,
            "ffmpeg_command": None,
            "ffmpeg_stdout": "",
            "ffmpeg_stderr": "",
        }
    if suffix not in AUDIO_SUFFIXES | VIDEO_SUFFIXES or kind == "video-audio" or suffix != ".wav":
        if not ffmpeg_path:
            raise RuntimeError("ffmpeg is required to process voice, compressed audio, and video inputs.")
        normalized_path = temp_dir / "normalized.wav"
        command = [
            ffmpeg_path,
            "-y",
            "-i",
            str(input_path),
            "-vn",
            "-ac",
            "1",
            "-ar",
            "16000",
            "-sample_fmt",
            "s16",
            str(normalized_path),
        ]
        completed = subprocess.run(command, capture_output=True, text=True, check=False)
        if completed.returncode != 0 or not normalized_path.exists():
            raise RuntimeError(_collapse(completed.stderr) or "ffmpeg failed to normalize the input media.")
        return {
            "audio_path": normalized_path,
            "used_ffmpeg": True,
            "ffmpeg_command": command,
            "ffmpeg_stdout": completed.stdout,
            "ffmpeg_stderr": completed.stderr,
        }
    raise RuntimeError(f"unsupported input suffix: {suffix}")


def _transcribe_wav_in_chunks(*, model: Any, audio_path: Path, chunk_seconds: float) -> Dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="gigaam-public-skill-chunks-") as chunk_dir_name:
        chunk_dir = Path(chunk_dir_name)
        with wave.open(str(audio_path), "rb") as source:
            params = source.getparams()
            frame_rate = source.getframerate()
            total_frames = source.getnframes()
            duration_seconds = 0.0 if frame_rate <= 0 else total_frames / float(frame_rate)
            frames_per_chunk = max(1, int(chunk_seconds * frame_rate))
            segments: List[Dict[str, Any]] = []
            chunk_index = 0
            while True:
                frames = source.readframes(frames_per_chunk)
                if not frames:
                    break
                chunk_index += 1
                chunk_path = chunk_dir / f"chunk-{chunk_index:04d}.wav"
                with wave.open(str(chunk_path), "wb") as target:
                    target.setparams(params)
                    target.writeframes(frames)
                raw_text = model.transcribe(str(chunk_path))
                text = _stringify_transcription(raw_text)
                start_seconds = (chunk_index - 1) * chunk_seconds
                end_seconds = min(duration_seconds, start_seconds + (len(frames) / float(frame_rate * params.sampwidth * params.nchannels)))
                segments.append(
                    {
                        "index": chunk_index,
                        "start_seconds": round(start_seconds, 3),
                        "end_seconds": round(end_seconds, 3),
                        "text": text,
                    }
                )
    return {
        "text": _collapse(" ".join(segment["text"] for segment in segments if segment["text"])),
        "segments": segments,
        "duration_seconds": round(duration_seconds, 3),
        "chunk_count": len(segments),
    }


def _write_probe(args: argparse.Namespace) -> int:
    model_name = _collapse(args.model) or _collapse(os.environ.get("GIGAAM_MODEL")) or DEFAULT_MODEL
    ffmpeg_path = _resolve_ffmpeg(args.ffmpeg_bin)
    allow_network = _allow_network(args.allow_network)
    payload = _runtime_probe_payload(model_name=model_name, ffmpeg_path=ffmpeg_path, allow_network=allow_network)
    _json_dump(Path(args.probe_output), payload)
    return 0 if payload["ready"] else 3


def _write_meta(*, path: Optional[str], payload: Dict[str, Any]) -> None:
    if path:
        _json_dump(Path(path), payload)


def _run_transcribe(args: argparse.Namespace) -> int:
    model_name = _collapse(args.model) or _collapse(os.environ.get("GIGAAM_MODEL")) or DEFAULT_MODEL
    chunk_seconds = float(args.chunk_seconds or os.environ.get("GIGAAM_MAX_CHUNK_SECONDS") or DEFAULT_CHUNK_SECONDS)
    allow_network = _allow_network(args.allow_network)
    ffmpeg_path = _resolve_ffmpeg(args.ffmpeg_bin)
    input_path = Path(args.input).resolve()
    if not input_path.exists():
        _write_meta(path=args.meta_output, payload={"generated_at": _iso_now(), "engine": "public-gigaam-skill-runtime", "success": False, "blocker": f"input file not found: {input_path}"})
        print(f"ERROR: input file not found: {input_path}", file=sys.stderr)
        return 2

    try:
        if not allow_network:
            os.environ.setdefault("HF_HUB_OFFLINE", "1")
            os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
        import gigaam  # type: ignore
        model = gigaam.load_model(model_name)
    except Exception as exc:
        blocker = _collapse(exc)
        _write_meta(path=args.meta_output, payload={"generated_at": _iso_now(), "engine": "public-gigaam-skill-runtime", "success": False, "blocked": True, "blocker": blocker, "safe_next_step": "Run bootstrap_gigaam_runtime.py, then retry transcription."})
        print(f"ERROR: {blocker}", file=sys.stderr)
        return 3

    with tempfile.TemporaryDirectory(prefix="gigaam-public-skill-") as temp_dir_name:
        temp_dir = Path(temp_dir_name)
        try:
            normalized = _normalize_audio(input_path=input_path, kind=args.kind, ffmpeg_path=ffmpeg_path, temp_dir=temp_dir)
            transcription = _transcribe_wav_in_chunks(model=model, audio_path=normalized["audio_path"], chunk_seconds=chunk_seconds)
        except Exception as exc:
            blocker = _collapse(exc)
            _write_meta(path=args.meta_output, payload={"generated_at": _iso_now(), "engine": "public-gigaam-skill-runtime", "success": False, "blocked": True, "blocker": blocker, "safe_next_step": "Inspect ffmpeg/runtime setup and retry."})
            print(f"ERROR: {blocker}", file=sys.stderr)
            return 4

    result = {
        "generated_at": _iso_now(),
        "engine": "public-gigaam-skill-runtime",
        "model": model_name,
        "input": {
            "path": str(input_path),
            "sha256": _sha256(input_path),
            "kind": args.kind,
            "title": args.title,
        },
        "runtime": {
            "python_executable": sys.executable,
            "ffmpeg_path": ffmpeg_path,
            "ffmpeg_used": normalized["used_ffmpeg"],
            "chunk_seconds": chunk_seconds,
            "allow_network_model_download": allow_network,
        },
        "transcription": transcription,
        "success": True,
    }

    text_path = Path(args.text_out)
    json_path = Path(args.json_out)
    summary_path = Path(args.summary_out)
    text_path.parent.mkdir(parents=True, exist_ok=True)
    text_path.write_text((transcription["text"] or "") + "\n", encoding="utf-8")
    _json_dump(json_path, result)
    _json_dump(summary_path, {
        "status": "ok",
        "input": str(input_path),
        "text_out": str(text_path),
        "json_out": str(json_path),
        "segment_count": transcription["chunk_count"],
    })
    _write_meta(path=args.meta_output, payload={"generated_at": _iso_now(), "engine": "public-gigaam-skill-runtime", "success": True, "text_out": str(text_path), "json_out": str(json_path), "summary_out": str(summary_path)})
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Standalone GigaAM-v3 runtime adapter for the public skill")
    subparsers = parser.add_subparsers(dest="command", required=True)

    probe = subparsers.add_parser("probe")
    probe.add_argument("--model")
    probe.add_argument("--ffmpeg-bin")
    probe.add_argument("--allow-network", action="store_true")
    probe.add_argument("--probe-output", required=True)

    transcribe = subparsers.add_parser("transcribe")
    transcribe.add_argument("--input", required=True)
    transcribe.add_argument("--kind", default="audio")
    transcribe.add_argument("--title")
    transcribe.add_argument("--language-hint", default="ru")
    transcribe.add_argument("--model")
    transcribe.add_argument("--chunk-seconds")
    transcribe.add_argument("--ffmpeg-bin")
    transcribe.add_argument("--allow-network", action="store_true")
    transcribe.add_argument("--text-out", required=True)
    transcribe.add_argument("--json-out", required=True)
    transcribe.add_argument("--summary-out", required=True)
    transcribe.add_argument("--meta-output")

    args = parser.parse_args()
    if args.command == "probe":
        return _write_probe(args)
    return _run_transcribe(args)


if __name__ == "__main__":
    raise SystemExit(main())

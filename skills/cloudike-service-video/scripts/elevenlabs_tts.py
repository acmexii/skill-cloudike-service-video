"""Generate scene MP3 and character timing. --check is offline."""
import argparse
import base64
import json
import os
from pathlib import Path
import subprocess
import sys
import urllib.error
import urllib.request

VOICE_ID = "1PdAOcPlPTz12RwMyFVp"


def load_key():
    key = os.environ.get("ELEVENLABS_API_KEY", "").strip()
    if key:
        return key
    default = Path(__file__).resolve().parents[4] / ".secrets/cloudike-video/elevenlabs.dpapi"
    path = Path(os.environ.get("ELEVENLABS_KEY_FILE", str(default))).resolve()
    if os.name != "nt" or not path.is_file():
        raise RuntimeError("Set ELEVENLABS_API_KEY or a valid Windows DPAPI key file.")
    env = os.environ.copy()
    env["CLOUDIKE_DPAPI_PATH"] = str(path)
    command = "$s=ConvertTo-SecureString -String ((Get-Content -Raw -LiteralPath $env:CLOUDIKE_DPAPI_PATH).Trim()); $b=[Runtime.InteropServices.Marshal]::SecureStringToBSTR($s); try {[Console]::Write([Runtime.InteropServices.Marshal]::PtrToStringBSTR($b))} finally {[Runtime.InteropServices.Marshal]::ZeroFreeBSTR($b)}"
    result = subprocess.run(["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", command], env=env, capture_output=True, text=True)
    if result.returncode or not result.stdout.strip():
        raise RuntimeError("Unable to decrypt local credential.")
    return result.stdout.strip()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--text-file", type=Path)
    parser.add_argument("--out-prefix", type=Path)
    args = parser.parse_args()
    key = load_key()
    if args.check:
        print("Credential available; offline check only. Voice: " + VOICE_ID)
        return
    if not args.text_file or not args.out_prefix:
        parser.error("--text-file and --out-prefix required")
    text = args.text_file.read_text(encoding="utf-8-sig").strip()
    if not text or len(text) > 5000:
        raise RuntimeError("Scene text must contain 1 to 5000 characters.")
    audio_path = Path(str(args.out_prefix) + ".mp3")
    timing_path = Path(str(args.out_prefix) + ".alignment.json")
    if audio_path.exists() or timing_path.exists():
        raise RuntimeError("Output exists; reuse or choose another prefix.")
    body = {"text": text, "model_id": "eleven_multilingual_v2", "voice_settings": {"stability": 0.5, "similarity_boost": 0.75, "style": 0.1, "use_speaker_boost": True}}
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}/with-timestamps?output_format=mp3_44100_128"
    request = urllib.request.Request(url, data=json.dumps(body).encode("utf-8"), headers={"xi-api-key": key, "Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            data = json.load(response)
    except urllib.error.HTTPError as error:
        raise RuntimeError(f"ElevenLabs HTTP {error.code}; no retry. Check authentication, voice access and quota.") from None
    except urllib.error.URLError:
        raise RuntimeError("ElevenLabs connection failed; no retry.") from None
    audio = base64.b64decode(data["audio_base64"], validate=True)
    timing = data.get("alignment") or data.get("normalized_alignment")
    if not audio or not timing or not timing.get("characters"):
        raise RuntimeError("Missing audio or timing; incomplete result not saved.")
    audio_path.parent.mkdir(parents=True, exist_ok=True)
    audio_path.write_bytes(audio)
    timing_path.write_text(json.dumps({"voice_id": VOICE_ID, "model_id": body["model_id"], "alignment": data.get("alignment"), "normalized_alignment": data.get("normalized_alignment")}, ensure_ascii=False, indent=2), encoding="utf-8")
    print("Saved audio and timing: " + str(args.out_prefix))


if __name__ == "__main__":
    try:
        main()
    except (RuntimeError, OSError, ValueError, KeyError) as error:
        print(str(error), file=sys.stderr)
        sys.exit(1)

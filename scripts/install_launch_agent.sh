#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
LABEL="com.recuerdame.salsa-practice"
PLIST_SRC="$ROOT/launchd/$LABEL.plist"
PLIST_DEST="$HOME/Library/LaunchAgents/$LABEL.plist"
LOG_DIR="$HOME/Library/Logs/recuerdame-salsa"
PYTHON="$(command -v python3)"

if [[ -z "$PYTHON" ]]; then
  echo "python3 not found in PATH" >&2
  exit 1
fi

if ! command -v yt-dlp >/dev/null 2>&1; then
  echo "Missing yt-dlp. Install with: brew install yt-dlp" >&2
  exit 1
fi
if ! command -v mpv >/dev/null 2>&1 && ! command -v afplay >/dev/null 2>&1; then
  echo "Need mpv (brew install mpv) or macOS afplay for playback." >&2
  exit 1
fi

mkdir -p "$LOG_DIR"
chmod +x "$ROOT/scripts/play_salsa.py" "$ROOT/scripts/daily_scheduler.py"

sed -e "s|REPLACE_PYTHON|$PYTHON|g" \
    -e "s|REPLACE_PROJECT|$ROOT|g" \
    -e "s|REPLACE_LOGS|$LOG_DIR|g" \
    "$PLIST_SRC" > "$PLIST_DEST"

launchctl bootout "gui/$(id -u)/$LABEL" 2>/dev/null || true
launchctl bootstrap "gui/$(id -u)" "$PLIST_DEST"
launchctl enable "gui/$(id -u)/$LABEL"

echo "Installed $PLIST_DEST"
echo "Logs: $LOG_DIR/salsa-practice.log"
echo ""
echo "Test playback now (3 songs):"
echo "  $PYTHON $ROOT/scripts/play_salsa.py"
echo ""
echo "Dry-run scheduler (pick time + wait — Ctrl+C to cancel):"
echo "  $PYTHON $ROOT/scripts/daily_scheduler.py"

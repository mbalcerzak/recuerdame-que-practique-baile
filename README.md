# Recuérdame que practiquemos baile

*Remember to dance.*

## About this project

**Recuérdame que practique baile** is a small, local helper for building a daily salsa habit. You do not open an app or set a fixed alarm: your Mac nudges you once a day by playing music, so practice fits into real life instead of waiting for the “perfect” hour.

Each day, between **12:00 and 15:00 (Europe/Madrid)**, the system picks a **random moment** in that window and plays **three salsa tracks** from YouTube. That is enough time to stretch, drill footwork, run through a shine, or simply move to the music—without committing to a full class.

Everything runs on your MacBook: scheduling via **launchd**, playback via **yt-dlp** and **mpv**. No cloud account, no Spotify developer setup, no API keys.

## Why this exists

Motivation is rarely about knowing *what* to do; it is about showing up when the day gets busy. A surprise playlist in the middle of the day breaks the loop of “later, later, mañana”—the same spirit as the project name: *recuérdame que practique baile*.

Three songs are intentional: long enough to feel like practice, short enough that excuses do not win. Consistency beats intensity. If you dance a little most days, the body remembers what the mind forgets.

You built this for yourself. Let the music find you.

## Setup

1. Install dependencies:

   ```bash
   brew install yt-dlp
   brew install mpv   # optional; macOS can use built-in afplay instead
   ```

2. Install the daily launch agent:

   ```bash
   chmod +x scripts/install_launch_agent.sh scripts/uninstall_launch_agent.sh
   ./scripts/install_launch_agent.sh
   ```

3. Test immediately (plays 3 songs; use `--songs 1` for a quick check):

   ```bash
   python3 scripts/play_salsa.py
   python3 scripts/play_salsa.py --songs 1
   ```

## How it works

- **launchd** starts `scripts/daily_scheduler.py` every day at **12:00 Madrid time**.
- The scheduler picks a random instant in the next **3 hours**, sleeps until then, and runs `scripts/play_salsa.py`.
- The player searches YouTube for salsa, builds a 3-track playlist, and **mpv** stops after the third song.

Logs: `~/Library/Logs/recuerdame-salsa/salsa-practice.log`

## Notes

- The Mac must be **awake** during the chosen window; if it is asleep, launchd runs when the machine wakes (still within 12:00–15:00 Madrid if you wake up before 15:00).
- **Spotify** was skipped on purpose: it needs a developer app, OAuth, Premium, and an active Spotify device. YouTube + yt-dlp is much simpler for local playback.
- Uninstall: `./scripts/uninstall_launch_agent.sh`

## Why Youtube?

The Spotify Web API can start playback only on an active Premium account with a connected device. For a small local reminder, YouTube search + mpv is the path of least resistance.

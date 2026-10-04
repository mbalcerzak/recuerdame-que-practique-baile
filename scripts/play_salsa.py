#!/usr/bin/env python3
"""Play salsa tracks from YouTube (yt-dlp + mpv, or afplay on macOS)."""

from __future__ import annotations

import argparse
import random
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

DEFAULT_SONG_COUNT = 3
YOUTUBE_EXTRACTOR_ARGS = "youtube:player_client=android,web"
SEARCH_QUERIES = [
    "salsa dura classic",
    "salsa timba",
    "salsa cubana",
    "eddie palmieri salsa",
    "hector lavoe salsa",
    "grupo niche salsa",
    "frankie ruiz salsa",
    "salsa romantica bachata practice",
]


def require_command(name: str) -> str:
    path = shutil.which(name)
    if not path:
        print(
            f"Missing '{name}'. Install with: brew install {name}",
            file=sys.stderr,
        )
        sys.exit(1)
    return path


def fetch_video_urls(yt_dlp: str, query: str, count: int) -> list[str]:
    search = f"ytsearch{count}:{query}"
    proc = subprocess.run(
        [
            yt_dlp,
            "--flat-playlist",
            "--print",
            "url",
            "--no-warnings",
            "--quiet",
            search,
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or f"yt-dlp failed for {search!r}")

    urls = [line.strip() for line in proc.stdout.splitlines() if line.strip()]
    if not urls:
        raise RuntimeError(f"No YouTube results for {query!r}")
    return urls[:count]


def play_with_mpv(mpv: str, playlist_urls: list[str], song_count: int) -> int:
    with tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".m3u",
        delete=False,
        encoding="utf-8",
    ) as playlist:
        for url in playlist_urls:
            playlist.write(url + "\n")
        playlist_path = Path(playlist.name)

    try:
        return subprocess.run(
            [
                mpv,
                f"--playlist={playlist_path}",
                "--no-video",
                "--really-quiet",
                "--keep-open=no",
                f"--playlist-end={song_count}",
                f"--ytdl-raw-options=extractor-args={YOUTUBE_EXTRACTOR_ARGS}",
            ],
            check=False,
        ).returncode
    finally:
        playlist_path.unlink(missing_ok=True)


def play_with_afplay(yt_dlp: str, afplay: str, playlist_urls: list[str]) -> int:
    with tempfile.TemporaryDirectory(prefix="salsa-practice-") as tmp:
        tmp_path = Path(tmp)
        for index, url in enumerate(playlist_urls, start=1):
            out_template = str(tmp_path / f"{index}.%(ext)s")
            dl = subprocess.run(
                [
                    yt_dlp,
                    "-f",
                    "bestaudio[ext=m4a]/bestaudio/best",
                    "--extractor-args",
                    YOUTUBE_EXTRACTOR_ARGS,
                    "-o",
                    out_template,
                    "--no-playlist",
                    "--no-warnings",
                    "--quiet",
                    url,
                ],
                check=False,
            )
            if dl.returncode != 0:
                print(f"Failed to download song {index}: {url}", file=sys.stderr)
                continue

            audio_files = sorted(tmp_path.glob(f"{index}.*"))
            if not audio_files:
                print(f"No audio file for song {index}", file=sys.stderr)
                continue

            print(f"Playing song {index}…", flush=True)
            play = subprocess.run([afplay, str(audio_files[0])], check=False)
            if play.returncode != 0:
                return play.returncode
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Play salsa tracks from YouTube.")
    parser.add_argument(
        "--songs",
        type=int,
        default=DEFAULT_SONG_COUNT,
        metavar="N",
        help=f"number of tracks to play (default: {DEFAULT_SONG_COUNT})",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    song_count = max(1, args.songs)

    yt_dlp = require_command("yt-dlp")
    mpv = shutil.which("mpv")
    afplay = shutil.which("afplay")
    if not mpv and not afplay:
        print(
            "Need mpv (brew install mpv) or macOS afplay for playback.",
            file=sys.stderr,
        )
        return 1

    query = random.choice(SEARCH_QUERIES)
    urls = fetch_video_urls(yt_dlp, query, song_count + 2)
    playlist_urls = urls[:song_count]

    player = "mpv" if mpv else "afplay (via yt-dlp download)"
    print(f"Playing {song_count} songs with {player} (search: {query!r})")
    for i, url in enumerate(playlist_urls, start=1):
        print(f"  {i}. {url}")

    if mpv:
        return play_with_mpv(mpv, playlist_urls, song_count)
    return play_with_afplay(yt_dlp, afplay, playlist_urls)


if __name__ == "__main__":
    raise SystemExit(main())

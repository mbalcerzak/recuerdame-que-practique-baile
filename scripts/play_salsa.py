#!/usr/bin/env python3
"""Play three salsa tracks from YouTube (via yt-dlp + mpv)."""

from __future__ import annotations

import random
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

SONG_COUNT = 3
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


def main() -> int:
    yt_dlp = require_command("yt-dlp")
    mpv = require_command("mpv")

    query = random.choice(SEARCH_QUERIES)
    # Fetch extras in case some URLs fail to play.
    urls = fetch_video_urls(yt_dlp, query, SONG_COUNT + 2)
    playlist_urls = urls[:SONG_COUNT]

    with tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".m3u",
        delete=False,
        encoding="utf-8",
    ) as playlist:
        for url in playlist_urls:
            playlist.write(url + "\n")
        playlist_path = Path(playlist.name)

    print(f"Playing {SONG_COUNT} songs (search: {query!r})")
    for i, url in enumerate(playlist_urls, start=1):
        print(f"  {i}. {url}")

    try:
        proc = subprocess.run(
            [
                mpv,
                f"--playlist={playlist_path}",
                "--no-video",
                "--really-quiet",
                "--keep-open=no",
                f"--playlist-start=1",
                f"--playlist-end={SONG_COUNT}",
            ],
            check=False,
        )
        return proc.returncode
    finally:
        playlist_path.unlink(missing_ok=True)


if __name__ == "__main__":
    raise SystemExit(main())

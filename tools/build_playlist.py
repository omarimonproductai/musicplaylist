#!/usr/bin/env python3
"""Upload a playlist's media to Cloudinary and generate its playlist JSON.

Reads files from incoming/<slug>/ (a manifest.csv plus media files), uploads
each media file to the Cloudinary account, and writes playlists/<slug>.json
with the resulting URLs, registering <slug> in playlists/index.json.

Usage:
    CLOUDINARY_URL=cloudinary://<api_key>:<api_secret>@dmtnhepkp \
        python3 tools/build_playlist.py <slug> --title "Visible title"

manifest.csv columns (header required):
    num,title,artist,youtube
Media files are matched to each row by the "num" prefix of the filename:
    <num>*.mp4 -> audio (resource_type=video)
    <num>*.txt -> lyrics (resource_type=raw)
    <num>*.lrc -> lrc    (resource_type=raw)
youtube is optional; missing media fields are simply omitted.
"""

import argparse
import csv
import glob
import json
import os
import re
import sys

import cloudinary
import cloudinary.uploader

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def find_file(folder, num, exts, exclude=()):
    for ext in exts:
        for path in sorted(glob.glob(os.path.join(folder, f"{num}*{ext}"))):
            if any(path.endswith(x) for x in exclude):
                continue
            return path
    return None


def upload(path, resource_type, folder):
    # use_filename + unique_filename=False keep the original filename as the
    # Cloudinary public_id (instead of a random string); folder groups each
    # playlist's assets and prevents same-named files across playlists from
    # overwriting each other.
    res = cloudinary.uploader.upload(
        path,
        resource_type=resource_type,
        folder=folder,
        use_filename=True,
        unique_filename=False,
        overwrite=True,
    )
    return res["secure_url"]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("slug", help="Playlist slug (folder name and JSON filename)")
    parser.add_argument("--title", required=True, help="Visible playlist title")
    parser.add_argument("--front", action="store_true",
                        help="Add the slug at the top of index.json instead of the end")
    args = parser.parse_args()

    if os.environ.get("CLOUDINARY_URL"):
        cloudinary.config()  # reads CLOUDINARY_URL
    elif os.environ.get("CLOUDINARY_API_KEY") and os.environ.get("CLOUDINARY_API_SECRET"):
        cloudinary.config(
            cloud_name=os.environ.get("CLOUDINARY_CLOUD_NAME", "dmtnhepkp"),
            api_key=os.environ["CLOUDINARY_API_KEY"],
            api_secret=os.environ["CLOUDINARY_API_SECRET"],
        )
    else:
        sys.exit(
            "Set CLOUDINARY_URL, or CLOUDINARY_API_KEY + CLOUDINARY_API_SECRET "
            "(+ optional CLOUDINARY_CLOUD_NAME, default dmtnhepkp)"
        )

    folder = os.path.join(ROOT, "incoming", args.slug)
    manifest = os.path.join(folder, "manifest.csv")
    if not os.path.isfile(manifest):
        sys.exit(f"Manifest not found: {manifest}")

    songs = []
    with open(manifest, newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            num = row["num"].strip()
            song = {"num": num, "title": row["title"].strip(), "artist": row["artist"].strip()}

            audio = find_file(folder, num, [".mp4", ".m4a"])
            if audio:
                # player.html derives the playable URL by swapping .mp4 -> .mp3,
                # so store the audio URL with a .mp4 extension (Cloudinary
                # transcodes the source on delivery).
                song["audio"] = re.sub(r"\.[A-Za-z0-9]+$", ".mp4", upload(audio, "video", args.slug))
            else:
                print(f"  ! no audio for {num} {song['title']}", file=sys.stderr)

            lyrics = find_file(folder, num, [".txt"], exclude=[".info.txt"])
            if lyrics:
                song["lyrics"] = upload(lyrics, "raw", args.slug)

            youtube = (row.get("youtube") or "").strip()
            if youtube:
                song["youtube"] = youtube

            lrc = find_file(folder, num, [".lrc"])
            if lrc:
                song["lrc"] = upload(lrc, "raw", args.slug)

            print(f"  ok {num} {song['title']}")
            songs.append(song)

    out = os.path.join(ROOT, "playlists", f"{args.slug}.json")
    with open(out, "w", encoding="utf-8") as fh:
        json.dump({"title": args.title, "songs": songs}, fh, indent=4, ensure_ascii=False)
        fh.write("\n")

    index_path = os.path.join(ROOT, "playlists", "index.json")
    with open(index_path, encoding="utf-8") as fh:
        index = json.load(fh)
    if args.slug not in index:
        index.insert(0, args.slug) if args.front else index.append(args.slug)
        with open(index_path, "w", encoding="utf-8") as fh:
            json.dump(index, fh, indent=2, ensure_ascii=False)
            fh.write("\n")

    print(f"Wrote {out} ({len(songs)} songs) and updated index.json")


if __name__ == "__main__":
    main()

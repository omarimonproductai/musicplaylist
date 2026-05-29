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
import sys

import cloudinary
import cloudinary.uploader

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def find_file(folder, num, ext):
    matches = sorted(glob.glob(os.path.join(folder, f"{num}*{ext}")))
    return matches[0] if matches else None


def upload(path, resource_type):
    res = cloudinary.uploader.upload(path, resource_type=resource_type)
    return res["secure_url"]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("slug", help="Playlist slug (folder name and JSON filename)")
    parser.add_argument("--title", required=True, help="Visible playlist title")
    args = parser.parse_args()

    if not os.environ.get("CLOUDINARY_URL"):
        sys.exit("CLOUDINARY_URL env var is required (cloudinary://key:secret@dmtnhepkp)")
    cloudinary.config()  # reads CLOUDINARY_URL

    folder = os.path.join(ROOT, "incoming", args.slug)
    manifest = os.path.join(folder, "manifest.csv")
    if not os.path.isfile(manifest):
        sys.exit(f"Manifest not found: {manifest}")

    songs = []
    with open(manifest, newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            num = row["num"].strip()
            song = {"num": num, "title": row["title"].strip(), "artist": row["artist"].strip()}

            audio = find_file(folder, num, ".mp4")
            if audio:
                song["audio"] = upload(audio, "video")
            else:
                print(f"  ! no audio for {num} {song['title']}", file=sys.stderr)

            lyrics = find_file(folder, num, ".txt")
            if lyrics:
                song["lyrics"] = upload(lyrics, "raw")

            youtube = (row.get("youtube") or "").strip()
            if youtube:
                song["youtube"] = youtube

            lrc = find_file(folder, num, ".lrc")
            if lrc:
                song["lrc"] = upload(lrc, "raw")

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
        index.append(args.slug)
        with open(index_path, "w", encoding="utf-8") as fh:
            json.dump(index, fh, indent=2, ensure_ascii=False)
            fh.write("\n")

    print(f"Wrote {out} ({len(songs)} songs) and updated index.json")


if __name__ == "__main__":
    main()

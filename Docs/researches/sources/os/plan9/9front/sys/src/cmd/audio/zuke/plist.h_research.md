# File Research: sources/os/plan9/9front/sys/src/cmd/audio/zuke/plist.h

Shared zuke playlist format and metadata header.

Key contents:
- Documents the intended playlist record layout.
- Defines one-letter field tags for album, artist, basename, composer, date, duration, format, image, title, track, path, and replaygain.
- Defines `Maxartist`.
- Defines `Meta`, including artist array, album/title/path/basename/image/file format, replaygain, duration, and embedded-image fields.
- Declares `printmeta()`.

Research notes:
- Comments mention a counted record format, while current `printmeta()` writes blank-line-delimited records.
- `Meta` fields are mostly borrowed pointers when parsed by `zuke.c`.

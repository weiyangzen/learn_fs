# File Research: sources/os/plan9/9front/sys/src/cmd/audio/zuke/mkplist.c

Playlist generator for zuke.

Key responsibilities:
- Recursively scans file/directory arguments, with bounded recursion and path normalization.
- Uses libtags to read metadata, duration, replaygain, embedded image info, and file format.
- Handles HTTP/HTTPS arguments as stream entries, using `icyget()` to retrieve ICY title/artist metadata.
- Optionally invokes `audio/moddec -r 0` to determine module-file duration.
- Uses worker procs to scan tags in parallel and a metadata thread to collect and sort tracks.
- Sorts tracks by path/artist/composer/date/album/track unless `-s` simple path sort is requested.
- Emits zuke playlist records via `printmeta()`.

Dependencies:
- Uses `tags.h`, Plan 9 thread channels, `plist.h`, and `icy.h`.

Research notes:
- Format names are mapped from libtags enum values to decoder names such as `mp3`, `ogg`, `flac`, `m4a`, `opus`, `wav`, or `mod`.
- Missing tags/durations are reported to stderr but do not necessarily exclude a track.

# File Research: sources/os/plan9/9front/sys/src/cmd/audio/zuke/plist.c

Zuke playlist metadata serializer.

Key responsibilities:
- Writes `Meta` fields as one-letter tagged lines to a `Biobuf`.
- Emits path and file format first.
- Emits all artists, optional album/title/composer/date/track, duration, replaygain values, and embedded image metadata.
- Terminates each record with a blank line.

Dependencies:
- Uses field tags and `Meta` from `plist.h`.

Research notes:
- The serializer is intentionally simple and pairs with `zuke.c` playlist parsing.

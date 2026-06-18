# File Research: sources/os/plan9/9front/sys/src/cmd/reform/shortcuts.c

Keyboard shortcut filter for Reform devices. Reads NUL-delimited keyboard records from stdin and writes filtered records to stdout.

Consumes control-key multimedia runes for brightness, mute, volume, media previous/next/play-pause, writing to `/dev/light`, `/dev/volume`, `/dev/audioctl`, or sending plumber messages.

Unrecognized input is passed through unchanged; records with only consumed shortcut runes are suppressed.

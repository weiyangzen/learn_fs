# File Research: sources/os/plan9/9front/sys/src/cmd/fortune.c

## Purpose
Prints a random fortune line, using or rebuilding an offset index for the default fortunes file.

## Key Elements
Opens a specified file or `/sys/games/lib/fortunes`; for the default file, uses `/sys/games/lib/fortunes.index` if current, otherwise creates/rebuilds it with 32-bit little-endian line offsets; selects a random indexed offset or uses reservoir sampling while scanning.

## Dependencies
Uses Plan 9 Bio, `Dir` mtimes, `truerand`, `ntruerand`, and `nrand`.

## Behavior/Risks
Index offsets are stored in four bytes, limiting practical indexed offsets. If another process is rewriting a too-short index, it falls back to scanning. Long fortune lines are truncated to the 2048-byte `choice` buffer.

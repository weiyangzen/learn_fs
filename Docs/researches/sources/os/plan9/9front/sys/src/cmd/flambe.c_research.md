# File Research: sources/os/plan9/9front/sys/src/cmd/flambe.c

## Purpose
Interactive flame graph viewer for Plan 9 profile data.

## Key Elements
Loads symbols from an executable with libmach, reads profile records from `pr\x0f` data files, decodes big-endian record fields, draws proportional call graph bars, supports hover details, click-to-zoom, reset, quit, resize, and plumbing a selected program counter to an editor location.

## Dependencies
Uses Plan 9 draw/thread/mouse/keyboard/plumb APIs and libmach symbol/file-line support.

## Behavior/Risks
Assumes profile records are well-formed and recursively traversable by `down`/`right` indices. Drawing stores clickable rectangles per record and aborts on corrupt indices. The profile frequency header drives displayed seconds.

# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmemdraw/poly.c

Draws polylines by drawing each segment with `memline`.

Key function:
- `mempoly`: iterates adjacent vertex pairs, applies requested end styles to only the first and last segment, and uses disc joins for internal segment ends.

Important behavior:
- Source point is tracked relative to the first vertex so texture/source alignment stays consistent across segments.

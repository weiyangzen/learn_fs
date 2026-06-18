# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmemdraw/unload.c

Copies raw pixels out of a `Memimage`.

Key function:
- `unloadmemimage`: validates rectangle and destination byte count, then copies each scan line to caller-provided storage.

Important behavior:
- Uses `bytesperline` for packed-image scan width.
- Does not do bit extraction beyond byte-range copying from `byteaddr`.

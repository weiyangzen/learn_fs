# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmemdraw/load.c

Loads raw uncompressed pixel bytes into a `Memimage`.

Key function:
- `_loadmemimage`: validates rectangle and byte count, then copies scan lines into image storage.

Important behavior:
- Handles sub-byte image depths with bit insertion masks at left and right rectangle edges.
- Uses direct `memmove` for byte-aligned full-line middle regions.
- Returns the consumed byte count or `-1` on invalid input.

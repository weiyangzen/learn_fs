# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmemdraw/read.c

Reads raw or compressed Plan 9 image files.

Key function:
- `readmemimage`: detects `compressed\n`, delegates to `creadmemimage` when present, otherwise parses raw image headers and loads image chunks.

Important behavior:
- Supports old ldepth and new channel-descriptor headers.
- Reads in chunks of at least 32 KiB or one scan line.
- Old image data is bit-inverted before loading.
- Uses `loadmemimage` for each chunk.

# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmemdraw/cread.c

Reads compressed Plan 9 image files into `Memimage`.

Key function:
- `creadmemimage`: parses compressed-image headers, allocates a destination image, reads compressed blocks, and calls `cloadmemimage`.

Important behavior:
- Supports both new textual channel descriptors and old ldepth headers.
- Uses `_compblocksize` to bound compressed block allocation.
- Old image data is bit-twiddled before decompression.
- Validates rectangle and per-block `maxy`/byte-count fields.

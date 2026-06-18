# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmemdraw/write.c

Writes a `Memimage` in compressed Plan 9 image format.

Key function:
- `writememimage`: unloads image data, emits a `compressed\n` header, compresses scan lines, and writes compressed blocks.

Compression behavior:
- Uses a sliding window of `NMEM` bytes and a hash table over `NMATCH` bytes.
- Emits literal dump runs and back-reference runs.
- Splits output into bounded compressed blocks with per-block `maxy` and byte count headers.

Important dependencies:
- Uses `unloadmemimage`, `chantostr`, `_compblocksize`, `write`, and Plan 9 image compression constants.

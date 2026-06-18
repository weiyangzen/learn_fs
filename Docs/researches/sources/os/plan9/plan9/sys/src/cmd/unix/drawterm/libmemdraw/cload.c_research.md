# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmemdraw/cload.c

Loads compressed image data into a `Memimage`.

Key function:
- `_cloadmemimage`: decodes the Plan 9 image compression format into the target rectangle.

Important behavior:
- Uses a circular history buffer of `NMEM` bytes.
- Bytes with high bit set encode literal runs; other bytes encode back-reference offset and match length.
- Validates rectangle containment, buffer length, and scan-line phase consistency.

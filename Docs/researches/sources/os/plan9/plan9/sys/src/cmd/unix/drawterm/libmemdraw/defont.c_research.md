# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmemdraw/defont.c

Builds a `Memsubfont` from embedded default font data.

Key function:
- `getmemdefont`: aligns `defontdata`, parses image header, wraps bitmap data in `Memdata`, creates a `Memimage`, decodes fontchar records, and returns an allocated subfont.

Important behavior:
- `Memdata.base` is set so the embedded byte array is not freed as allocated pixel memory.
- Uses `_unpackinfo` from libdraw default font support.

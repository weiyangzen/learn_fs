# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmemdraw/openmemsubfont.c

Loads a subfont file into memory.

Key function:
- `openmemsubfont`: opens a file, reads its image with `readmemimage`, parses font header and packed fontchar records, unpacks metrics, and returns a `Memsubfont`.

Important behavior:
- Cleans up image and packed buffer on error.
- Uses `_unpackinfo` and `allocmemsubfont`.
- The success path returns without closing the file explicitly in this source, matching the original minimal implementation pattern.

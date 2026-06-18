# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmemdraw/mkcmap.c

Generator for `cmap.c`.

Key functions:
- `mkcmap`: builds `cmap2rgb` and `rgb2cmap` tables using libdraw conversion functions.
- `main`: prints C source for a static `Memcmap`, with an Inferno include variant under `-i`.

Important behavior:
- Calls `memimageinit` before generating tables.
- Output format matches the checked-in generated `cmap.c`.

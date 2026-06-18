# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmemdraw/subfont.c

Allocates and frees `Memsubfont` structures.

Key functions:
- `allocmemsubfont`: stores metadata, fontchar array, bitmap image, and optional duplicated name.
- `freememsubfont`: frees fontchar data, backing image, and the subfont object.

Important note:
- `freememsubfont` does not free `f->name` in this file, even though allocation uses `strdup`; that is an ownership/leak behavior present in this source.

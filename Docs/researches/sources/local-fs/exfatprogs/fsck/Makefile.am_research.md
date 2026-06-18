# File Research: sources/local-fs/exfatprogs/fsck/Makefile.am

This Automake file builds the `fsck.exfat` program.

It sets common C flags with warnings, generated `config.h`, the project `include` path, and `-fno-common`. The binary links against the internal static library `$(top_builddir)/lib/libexfat.a`.

The program source list is tightly scoped to the checker implementation and repair UI:
- `fsck.c`
- `repair.c`
- `fsck.h`
- `repair.h`

This file has no conditional build logic; `fsck.exfat` is always listed in `sbin_PROGRAMS`.

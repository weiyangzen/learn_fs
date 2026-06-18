# File Research: sources/local-fs/exfatprogs/mkfs/Makefile.am

This Automake file builds the `mkfs.exfat` program.

It sets warnings, generated `config.h`, the project include path, `-fno-common`, and `$(BLKID_CFLAGS)`. The binary links against internal `libexfat.a` and `$(BLKID_LIBS)` for existing-signature detection and library version reporting.

The program source list is:
- `mkfs.c`
- `upcase.c`
- `mkfs.h`
- `crc.c`

There is no conditional source selection in this file; `mkfs.exfat` is always installed via `sbin_PROGRAMS`.

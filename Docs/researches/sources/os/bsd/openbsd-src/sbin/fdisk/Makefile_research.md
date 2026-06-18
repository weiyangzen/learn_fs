# File Research: sources/os/bsd/openbsd-src/sbin/fdisk/Makefile

## Purpose
Builds OpenBSD `fdisk`.

## Key Contents
- Sources include command handling, user interface, disk I/O, MBR, partition formatting, manual embedding, and GPT support.
- Generates `manual.c` from `fdisk.8` compressed into a byte array, or a placeholder when `NOMAN` is set.
- Links with `libutil`.
- Defines `HAS_MBR` on amd64, i386, and landisk.
- Adds a SH architecture workaround disabling builtin memcpy.

## Notes
The Makefile embeds the manual so the interactive command can display it through a pager.

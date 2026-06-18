# File Research: sources/os/bsd/dragonflybsd/sys/vfs/msdosfs/msdosfs_conv.c

## Scope

Implements MSDOSFS filename and timestamp conversion helpers for DOS 8.3 names, VFAT long filenames, local character sets, Unicode/Win95 entries, and multi-slot long-name assembly.

## APIs And Behavior

- Static translation tables map ISO-8859-1/local bytes to CP850/DOS bytes, reverse-map DOS to local, and implement case folding.
- `dos2unixfn()` converts an 8.3 DOS name to a Unix-visible name, honoring escaped first `0xe5` and lowercase flags.
- `unix2dosfn()` converts local names to DOS 8.3 form, inserts generation suffixes, handles invalid/skipped characters, extension detection, multibyte boundaries, and `SLOT_E5`.
- `unix2winfn()` creates one VFAT long-name slot.
- `win2unixfn()` converts a VFAT long-name slot into local bytes and feeds `mbnambuf`.
- `winChkName()` compares a reconstructed long name case-insensitively.
- `winChksum()`, `winSlotCnt()`, and `winLenFixup()` support LFN slot management.
- `dos2unixchr()`, `unix2doschr()`, `win2unixchr()`, and `unix2winchr()` route through iconv when enabled, otherwise use built-in tables.
- `mbnambuf_init()`, `mbnambuf_write()`, and `mbnambuf_flush()` assemble multi-slot long names.

## Dependencies

Uses `direntry.h`, `bpb.h`, `msdosfsmount.h`, kernel iconv hooks, and DragonFly dirent/timing headers.

## Risks And Invariants

LFN assembly requires strictly decreasing slot IDs and checksum agreement. Multibyte truncation uses `mbsadjpos()` to avoid splitting encoded characters. DOS short-name generation must preserve FAT’s deleted-entry sentinel and disallow names made only of spaces/dots.

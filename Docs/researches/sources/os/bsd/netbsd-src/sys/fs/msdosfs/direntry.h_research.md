# File Research: sources/os/bsd/netbsd-src/sys/fs/msdosfs/direntry.h

## Purpose
Defines FAT short directory entries, Win95 long-name entries, timestamp bit layouts, filename conversion prototypes, and long-name checksum helpers.

## Main Contents
- `struct direntry` mirrors the 32-byte FAT directory entry: 8.3 name, attributes, creation/access/modify timestamps, FAT32 high cluster, low start cluster, and file size.
- Defines slot markers for empty, deleted, and escaped 0xe5 first character.
- Defines attribute bits for readonly, hidden, system, volume label, directory, and archive.
- `msdos_dirchar()` returns a character from the 8.3 name/extension aggregate.
- `struct winentry` mirrors Win95 long filename slots with sequence/count, UTF-16 name parts, attributes, checksum, and reserved fields.
- Defines long-name constants `WIN_LAST`, `WIN_CNT`, `ATTR_WIN95`, and `WIN_CHARS`.
- Defines DOS time/date masks and shifts.
- Declares DOS/Unix timestamp conversion, 8.3 conversion, long-name conversion, checksum, and slot-count routines.

## Dependencies
Uses fixed-width integer types and, for prototypes, NetBSD kernel or `MAKEFS` contexts.

## Risks and Notes
The on-disk structs intentionally expose byte arrays for little-endian fields. Long filename functions depend on reading Win95 slots in reverse order and verifying short-name checksums.

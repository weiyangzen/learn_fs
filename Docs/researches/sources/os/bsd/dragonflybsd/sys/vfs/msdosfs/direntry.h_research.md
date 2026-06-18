# File Research: sources/os/bsd/dragonflybsd/sys/vfs/msdosfs/direntry.h

## Scope

Defines FAT short directory entries, Win95 long filename entries, directory attribute constants, DOS date/time bit fields, and filename conversion prototypes.

## Data Structures And Constants

- `struct direntry` describes an 8.3 directory slot: name, attributes, NT lowercase flags, create/access/modify times, high/low cluster fields, and file size.
- Defines slot markers for empty, deleted, and escaped `0xe5` first character.
- Defines attribute bits for readonly, hidden, system, volume, directory, and archive.
- Defines lowercase flags `LCASE_BASE` and `LCASE_EXT`.
- `struct winentry` describes a VFAT long-name slot with order/checksum and three UTF-16 name parts.
- Defines `WIN_CHARS` and `WIN_MAXLEN`.
- Defines DOS packed time/date masks and shifts.
- Declares long-name buffer `mbnambuf` and conversion helpers for DOS, Unix, and Win95 names.

## Dependencies

Kernel or makefs consumers need `struct msdosfsmount` and `struct dirent`.

## Risks And Invariants

Long filename slots must be processed in reverse order and validated by checksum. Short directory entries use packed little-endian fields and special first-byte conventions that conversion code must preserve.

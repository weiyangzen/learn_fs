# File Research: sources/os/bsd/freebsd-src/sys/fs/msdosfs/msdosfs_conv.c

Implements filename and character conversion for msdosfs, including DOS 8.3 names, Win95/VFAT long filenames, local charset conversion, and UTF-16 handling.

Main responsibilities:
- Converts DOS short names to Unix names with optional lowercase handling.
- Converts Unix names to DOS 8.3 names, including generation suffixes like `~1`.
- Creates and validates VFAT long-name directory entries.
- Reassembles VFAT long-name entries into `dirent` names.
- Computes VFAT short-name checksums and LFN slot counts.
- Provides helper buffer management for multi-byte LFN assembly.

Key implementation details:
- Static translation tables map ISO-8859-1/local bytes to CP850-style DOS bytes and back, plus upper/lowercase tables.
- If `MSDOSFSMNT_KICONV` is active and `msdosfs_iconv` is available, conversions use kernel iconv handles from the mount.
- `unix2dosfn()` rejects names consisting only of spaces/dots and disallowed characters, handles `"."`/`".."`, splits extension rules, inserts generation numbers, and remaps leading `0xe5` to `SLOT_E5`.
- `unix2winfn()` writes one VFAT LFN slot at a time, trims trailing spaces/dots, handles UTF-16 surrogate pairs, and marks the last slot with `WIN_LAST`.
- `win2unixfn()` validates slot sequence and checksum, rejects embedded slash, handles surrogate pairs crossing slot boundaries, and appends slot text to `mbnambuf`.
- `winChkName()` compares requested names case-insensitively through UTF-16 conversion.
- `mbnambuf_write()` expects descending slot ids and shifts variable-width substrings to reconstruct full names.

Important dependencies:
- Uses `direntry.h` LFN/short-entry structures and `msdosfsmount.h` charset flags/handles.
- Exposes conversion routines declared in `direntry.h`.

Notable risks and edge cases:
- VFAT long names are case-insensitive for lookup even when preserving case.
- Trailing spaces and dots are dropped for Win95 long-name slot calculations.
- Invalid or unconvertible characters become `?`, `_`, or cause conversion failure depending on path.
- Surrogate-pair handling spans adjacent LFN slots, which is easy to break if slot ordering changes.

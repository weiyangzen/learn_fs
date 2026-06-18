# File Research: sources/local-fs/jfsutils/libfs/uniupr.c

This file contains Unicode uppercase mapping tables for JFS Unicode name handling.

Contents:
- `UniUpperTable[512]` maps the first 512 code points by signed deltas.
- Static range tables cover Greek, Cyrillic, extended Cyrillic, extended Latin/Greek, and wide Latin.
- `UniUpperRange[]` ties range starts/ends to the relevant signed-delta table and terminates with `{0, 0, 0}`.

Integration points:
- Includes `jfs_unicode.h`, which defines `struct UNICASERANGE` and likely consumes `UniUpperTable`/`UniUpperRange`.
- No functions are defined here; it is table data for case-insensitive Unicode comparisons or normalization elsewhere in libfs/fsck.

Notes:
- The mappings are static and limited to the Unicode-era table embedded in this source.
- Signed deltas encode uppercase conversion compactly; zero means no mapping.

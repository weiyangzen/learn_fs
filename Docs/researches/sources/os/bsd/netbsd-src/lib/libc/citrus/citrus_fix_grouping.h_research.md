# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_fix_grouping.h

Compatibility helper for locale grouping strings.

Key behavior:
- Defines portable locale grouping value range: 0..126 and no-further-grouping value 127.
- If platform `CHAR_MAX` differs from 127, `_citrus_fixup_char_max_md` rewrites byte value 127 in grouping strings to `CHAR_MAX`.
- If `CHAR_MAX` already equals 127, the fixup macro is a no-op.

Used by numeric and monetary locale loaders after reading compiled grouping strings.

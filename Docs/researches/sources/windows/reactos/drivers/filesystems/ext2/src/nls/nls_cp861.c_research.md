# File Research: sources/windows/reactos/drivers/filesystems/ext2/src/nls/nls_cp861.c

Purpose: Generated NLS module for DOS/OEM code page 861, supporting Icelandic-specific characters plus the common DOS graphics repertoire.

Core structures and data:
- `charset2uni[256]` maps high bytes to Icelandic/Nordic Latin letters including eth/thorn variants, accented vowels, DOS line drawing, block elements, Greek/math symbols, and `U+0192`.
- Reverse pages `page00`, `page01`, `page03`, `page20`, `page22`, `page23`, and `page25` cover Latin extended, Greek, math, technical, and graphics mappings.
- `charset2lower` and `charset2upper` encode Icelandic case relationships in CP861 byte space.

Important behavior:
- `uni2char()` rejects absent reverse pages and zero entries; successful conversions always emit one byte.
- `char2uni()` returns one byte consumed for valid mappings and rejects zero-valued entries.
- The module registers charset `"cp861"` with no alias.

Dependencies and interfaces:
- Uses the common Linux kernel NLS table interface and module macros.
- No external conversion backend is loaded.

Design notes and risks:
- Icelandic letters such as eth and thorn are table-driven; incorrect case tables can break case-insensitive filename comparisons.
- The reverse dispatch includes sparse pages, so omitted initializer entries rely on C zero-fill.
- `char2uni()` lacks an internal input-length guard and assumes its caller provides a valid byte pointer.

# File Research: sources/windows/reactos/drivers/filesystems/ext2/src/nls/nls_iso8859-4.c

This file implements the ISO-8859-4 NLS table registered as `iso8859-4`, covering Baltic/Nordic Latin mappings.

The byte-to-Unicode table maps ISO-8859-4-specific characters such as A/E/I/O/U macron, ogonek, cedilla, and Baltic letters into Unicode. Reverse lookup is provided through `page00`, `page01`, and `page02`.

`uni2char` is exact-only and rejects unmapped Unicode. `char2uni` rejects bytes whose table entry is zero, including NUL and undefined character positions.

The case conversion tables encode single-byte upper/lower mappings for the charset and are used through `nls_table.charset2lower` and `charset2upper`.

Research notes: no runtime allocation or state; behavior is stable and table-driven.

# File Research: sources/windows/reactos/drivers/filesystems/ext2/src/nls/nls_cp863.c

Purpose: Generated NLS module for DOS/OEM code page 863, a Canadian French code page with DOS graphics and symbols.

Core structures and data:
- `charset2uni[256]` maps high bytes to French accented letters, currency/punctuation, `U+2017`, box drawing, block elements, and Greek/math symbols.
- Reverse lookup pages are `page00`, `page01`, `page03`, `page20`, `page22`, `page23`, and `page25`.
- `charset2lower` and `charset2upper` fold ASCII plus the CP863 Latin accented letters.

Important behavior:
- `uni2char()` returns one encoded byte for exact reverse mappings and `-EINVAL` for unmapped code points.
- `char2uni()` consumes one byte and rejects `0x0000` table values.
- The registered charset is `"cp863"` with no alias.

Dependencies and interfaces:
- Implements the common Linux `struct nls_table` callback surface.
- No mutable conversion state exists after module registration.

Design notes and risks:
- Some CP863 byte values map to symbols rather than Latin letters, so reverse table page coverage extends into Greek/math and box drawing Unicode pages.
- The byte-level case tables are not equivalent to Unicode locale-aware folding.
- Generated table order is critical; a shifted initializer would corrupt many mappings without changing control flow.

# File Research: sources/windows/reactos/drivers/filesystems/ext2/src/nls/nls_cp862.c

Purpose: Generated NLS module for DOS/OEM code page 862, used for Hebrew byte-to-Unicode conversion with DOS graphics symbols.

Core structures and data:
- `charset2uni[256]` maps bytes `0x80-0x9a` to Hebrew letters `U+05D0..U+05EA`, then maps remaining high bytes to Latin punctuation, currency, box drawing, Greek/math symbols, and block glyphs.
- Reverse pages include `page00`, `page01`, `page03`, `page05`, `page20`, `page22`, `page23`, and `page25`.
- `page05` is the Hebrew reverse page mapping Unicode Hebrew letters back to CP862 bytes.
- Case tables are mostly ASCII/symbol identity; Hebrew has no upper/lower case folding.

Important behavior:
- `uni2char()` supports exact one-byte mappings through the reverse page table; no shaping, bidi processing, or normalization is performed.
- `char2uni()` maps one byte and rejects zero entries.
- The module registers `"cp862"` with no alias.

Dependencies and interfaces:
- Standard self-contained Linux NLS table, using `register_nls()` and `unregister_nls()` for lifecycle.
- No Hebrew-specific runtime library dependency exists; all behavior is static table lookup.

Design notes and risks:
- Hebrew text direction and presentation are outside this module; it only maps byte values to Unicode code points.
- Sparse reverse pages and zero sentinels make undefined bytes and Unicode NUL invalid.
- Filename equality behavior depends on the byte-level case tables, which intentionally do not fold Hebrew letters.

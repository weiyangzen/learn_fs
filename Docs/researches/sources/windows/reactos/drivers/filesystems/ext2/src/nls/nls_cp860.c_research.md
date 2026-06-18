# File Research: sources/windows/reactos/drivers/filesystems/ext2/src/nls/nls_cp860.c

Purpose: Generated NLS module for DOS/OEM code page 860, primarily Portuguese, with standard DOS graphics and mathematical symbols.

Core structures and data:
- `charset2uni[256]` maps high bytes to Portuguese accented Latin letters, DOS line/box drawing characters, Greek/math symbols, block glyphs, and punctuation such as `U+20A7`.
- Reverse pages include `page00`, `page03`, `page20`, `page22`, `page23`, and `page25`.
- `page_uni2charset[256]` dispatches Latin/punctuation, Greek, superscript/currency, math, technical symbol, and box/block pages.
- Case tables fold ASCII and the CP860 Latin accented pairs; Greek/math/box glyphs mostly remain identity or zero when undefined.

Important behavior:
- `uni2char()` performs exact one-byte reverse lookup through the page dispatch table.
- `char2uni()` indexes `charset2uni` and rejects `0x0000`.
- The NLS table is registered as `"cp860"` with no alias.

Dependencies and interfaces:
- Standard generated Linux NLS module shape; only NLS registration/unregistration touches global framework state.
- No Ext2 metadata logic appears in this file; it supplies conversion callbacks consumed by filesystem code elsewhere.

Design notes and risks:
- CP860's reverse mapping spans more Unicode pages than many Latin codepages because of Greek and math symbols inherited from DOS glyph sets.
- Case folding is byte-oriented and cannot implement Unicode normalization or decomposition.
- Generated table drift can make filenames fail to round-trip between on-disk bytes and Unicode names.

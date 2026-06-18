# File Research: sources/windows/reactos/drivers/filesystems/ext2/src/nls/nls_cp869.c

Purpose: Generated NLS module for DOS/OEM code page 869, a Greek code page.

Core structures and data:
- `charset2uni[256]` includes undefined high-byte holes, Greek capitals and lowercase letters, tonos/dialytika variants, punctuation, box drawing, and block characters.
- Reverse pages `page00`, `page03`, `page20`, and `page25` map Latin/punctuation, Greek, punctuation dashes/quotes, and drawing/block glyphs back to CP869.
- `charset2lower` and `charset2upper` encode Greek byte-level case pairs plus ASCII folding.

Important behavior:
- `uni2char()` accepts only exact Unicode-to-byte mappings; unmapped Greek forms or decomposed accents fail.
- `char2uni()` rejects bytes whose forward table entry is zero, including several undefined bytes in the `0x80` range.
- The module registers charset `"cp869"` with no alias.

Dependencies and interfaces:
- Standard Linux NLS callback implementation and module lifecycle.
- No external Greek normalization or locale handling is involved.

Design notes and risks:
- Greek precomposed accented forms are table entries; decomposed Unicode sequences do not round-trip through this module.
- Undefined high-byte positions must remain zero to avoid accepting invalid on-disk filename bytes.
- Case folding is byte-oriented and generated, not full Unicode case folding.

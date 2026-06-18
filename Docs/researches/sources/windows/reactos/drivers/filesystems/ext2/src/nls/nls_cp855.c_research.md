# File Research: sources/windows/reactos/drivers/filesystems/ext2/src/nls/nls_cp855.c

Purpose: Generated NLS module for DOS/OEM code page 855, a Cyrillic code page, wired into the ReactOS Ext2 driver's Linux-style NLS interface.

Core structures and data:
- `charset2uni[256]` maps ASCII/control bytes directly and maps high bytes to Cyrillic letters, box drawing, block elements, `U+2116` numero sign, and selected punctuation.
- Reverse pages `page00`, `page04`, `page21`, and `page25` support Unicode-to-CP855 lookup for Latin/punctuation, Cyrillic, numero sign, and drawing/block glyphs.
- `page_uni2charset[256]` points only those Unicode high pages at populated reverse arrays.
- `charset2lower` and `charset2upper` encode CP855's alternating Cyrillic case pairs plus ASCII case folding.

Important behavior:
- `uni2char()` performs exact one-byte reverse mapping through `page_uni2charset`; unmapped entries and zero results return `-EINVAL`.
- `char2uni()` consumes one byte and rejects `charset2uni` entries equal to zero.
- The module registers charset `"cp855"` with no alias.

Dependencies and interfaces:
- Standard Linux NLS module pattern using `<linux/nls.h>` and errno-style negative returns.
- Module lifecycle is limited to `register_nls(&table)` and `unregister_nls(&table)`.

Design notes and risks:
- CP855's case tables are data-critical because many Cyrillic upper/lower byte pairs are not contiguous in simple ASCII style.
- Reverse mapping depends on exact page dispatch; a wrong `page04` or `page21` pointer would reject or misencode whole Unicode ranges.
- No normalization or transliteration is attempted; only exact Unicode mappings are accepted.

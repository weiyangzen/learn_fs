# File Research: sources/windows/reactos/drivers/filesystems/ext2/src/nls/nls_cp864.c

Purpose: Generated NLS module for DOS/OEM code page 864, covering Arabic-oriented byte mappings, Arabic presentation forms, Arabic-Indic digits, punctuation, and DOS graphics.

Core structures and data:
- `charset2uni[256]` maps ASCII/control bytes, selected DOS graphics, Arabic punctuation (`U+060C`, `U+061B`, `U+061F`), Arabic-Indic digits `U+0660..U+0669`, tatweel/shadda, and many Arabic presentation forms in the `U+FE7D..U+FEFC` range.
- Reverse pages include `page00`, `page03`, `page06`, `page22`, `page25`, and `pagefe`.
- `page06` maps Arabic punctuation/digits/marks back to CP864.
- `pagefe` maps Arabic presentation forms back to CP864 byte values.
- Case tables are mostly identity/zero because Arabic has no upper/lower case; ASCII still folds normally.

Important behavior:
- `uni2char()` is exact and one-byte only; it does not compose/decompose Arabic presentation forms.
- `char2uni()` rejects undefined byte positions where the forward table stores `0x0000`.
- The registered charset is `"cp864"` with no alias.

Dependencies and interfaces:
- Self-contained Linux-style NLS table module.
- No shaping engine, bidi engine, or external charset backend is involved.

Design notes and risks:
- CP864 maps many bytes to Arabic presentation-form code points rather than base Arabic letters, so normalization differences can make Unicode inputs unencodable.
- Several forward table positions are undefined; those bytes fail conversion instead of substituting replacement characters.
- The reverse dispatch has a long mostly-null `page_uni2charset[256]` with a late `pagefe` entry; preserving high-page alignment is essential.

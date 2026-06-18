# File Research: sources/os/linux/linux/fs/nls/mac-roman.c

Implements the `macroman` NLS codepage module.

Key behavior:
- Provides generated Mac Roman mappings for ASCII, Western European Latin characters, punctuation, math symbols, ligatures, and the Apple private-use glyph.
- Reverse lookup includes pages `00`, `01`, `02`, `03`, `20`, `21`, `22`, `25`, `f8`, and `fb`; page `fb` handles `fb01` and `fb02` ligatures.
- `uni2char()` encodes only exact Unicode-to-byte mappings and returns `-EINVAL` otherwise.
- `char2uni()` decodes a single byte and rejects `0x0000`.
- Registers charset name `macroman`.

Important interactions:
- This is the base Mac Roman variant that the Icelandic, Romanian, and Turkish modules resemble structurally.
- Used by filesystem NLS users that need legacy Mac Roman filename translation.

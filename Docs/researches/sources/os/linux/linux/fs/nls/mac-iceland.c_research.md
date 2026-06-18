# File Research: sources/os/linux/linux/fs/nls/mac-iceland.c

Implements the `maciceland` NLS codepage module.

Key behavior:
- Provides generated Mac Iceland byte-to-Unicode and Unicode-to-byte mappings.
- The forward map covers ASCII plus Mac Iceland extended Latin, punctuation, math symbols, Icelandic letters, the Apple private-use glyph `0xf8ff`, and related modifier marks.
- Reverse lookup uses populated Unicode pages `00`, `01`, `02`, `03`, `20`, `21`, `22`, `25`, and `f8`.
- `char2uni()` rejects bytes mapping to `0x0000`; `uni2char()` only accepts exact reverse mappings.
- Registers charset name `maciceland`.

Important interactions:
- Follows the standard Linux NLS module shape used by filesystem filename conversion.
- Case conversion tables are generated data supplied through `struct nls_table`, not computed dynamically.

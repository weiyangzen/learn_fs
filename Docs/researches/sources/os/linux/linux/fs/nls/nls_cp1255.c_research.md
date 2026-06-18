# File Research: sources/os/linux/linux/fs/nls/nls_cp1255.c

Implements the `cp1255` Hebrew NLS codepage module, with an `iso8859-8` alias.

Key behavior:
- Provides CP1255 mappings for Hebrew letters, Hebrew marks, punctuation, and common Windows symbols.
- Forward map includes Hebrew Unicode page `05` entries and undefined bytes as `0x0000`.
- Reverse lookup uses pages `00`, `01`, `02`, `05`, `20`, and `21`.
- Registers charset name `cp1255` and alias `iso8859-8`.
- Declares `MODULE_ALIAS_NLS(iso8859-8)` so module autoload can satisfy that alias.

Important interactions:
- `find_nls()` in `nls_base.c` can match either `.charset` or `.alias`, so callers asking for `iso8859-8` can receive this table.
- The file describes both ISO-8859-8 and CP1255, but the actual table contains Windows CP1255-specific positions as well.

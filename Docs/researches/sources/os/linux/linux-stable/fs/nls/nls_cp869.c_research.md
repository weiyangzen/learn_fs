# File Research: sources/os/linux/linux-stable/fs/nls/nls_cp869.c

Implements Linux NLS support for DOS codepage `cp869`, described as Greek. It is built through `CONFIG_NLS_CODEPAGE_869`.

Key contents:
- `charset2uni[256]` maps cp869 Greek bytes, ASCII, symbols, and drawing characters to Unicode.
- Reverse pages are `page00`, `page03`, `page20`, and `page25`.
- Case tables cover Greek and ASCII mappings that are representable in cp869.
- `uni2char()` performs exact Unicode-to-byte lookup through `page_uni2charset`.
- `char2uni()` maps one byte through `charset2uni`.
- Registers `.charset = "cp869"`.

Important behavior:
- Similar in role to cp737 but with a different Greek DOS mapping.
- The module provides raw charset conversion only; it does not normalize Greek accents or compatibility forms beyond explicit table entries.

# File Research: sources/os/linux/linux-stable/fs/nls/nls_cp855.c

Implements Linux NLS support for DOS codepage `cp855`, described as Cyrillic. It is selected by `CONFIG_NLS_CODEPAGE_855`.

Key contents:
- `charset2uni[256]` maps cp855 Cyrillic bytes plus ASCII and DOS drawing/symbol bytes to Unicode.
- Reverse pages are `page00`, `page04`, `page21`, and `page25`.
- `page04` covers Cyrillic Unicode mappings; `page21` and `page25` cover selected symbols and box/block characters.
- Case tables encode Cyrillic upper/lower relationships in cp855 byte values.
- `uni2char()` is exact and sparse; unmapped Unicode returns `-EINVAL`.
- `char2uni()` maps one byte and rejects a resulting `0x0000`.
- Registers `.charset = "cp855"`.

Important behavior:
- Provides legacy Cyrillic DOS filename conversion for filesystems using the Linux NLS API.
- There is no normalization or cross-codepage fallback; callers must choose the right NLS table at mount/configuration time.

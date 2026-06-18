# File Research: sources/os/linux/linux-stable/fs/nls/nls_cp850.c

Implements Linux NLS support for DOS codepage `cp850`, described as Europe. It is selected by `CONFIG_NLS_CODEPAGE_850`.

Key contents:
- `charset2uni[256]` covers cp850 Western European Latin characters, drawing characters, and symbols.
- Reverse pages are `page00`, `page01`, `page20`, and `page25`.
- `charset2lower` / `charset2upper` provide codepage-local case mappings, including accented Latin pairs.
- `uni2char()` performs exact sparse reverse lookup and returns `-ENAMETOOLONG` for no output space or `-EINVAL` for unmapped Unicode.
- `char2uni()` maps one byte and rejects byte `0x00`.
- Registers `.charset = "cp850"` with description `NLS Codepage 850 (Europe)`.

Important behavior:
- This is one of the common FAT/DOS filename codepages for Western Europe.
- The reverse table includes only characters that can be encoded exactly in cp850; no transliteration is attempted.

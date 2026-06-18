# File Research: sources/os/linux/linux-stable/fs/nls/nls_cp862.c

Implements Linux NLS support for DOS codepage `cp862`, described as Hebrew. It is selected by `CONFIG_NLS_CODEPAGE_862`.

Key contents:
- `charset2uni[256]` maps cp862 bytes to ASCII, Hebrew letters, Latin/symbol entries, and DOS drawing characters.
- Reverse pages are `page00`, `page01`, `page03`, `page05`, `page20`, `page22`, `page23`, and `page25`.
- `page05` contains the Hebrew Unicode reverse mappings.
- Case tables mainly cover ASCII and representable Latin/Greek style mappings; Hebrew letters do not use case.
- `uni2char()` returns one byte only for exact table hits.
- `char2uni()` decodes one input byte and rejects NUL.
- Registers `.charset = "cp862"`.

Important behavior:
- Provides Hebrew DOS filename conversion without bidi processing; it is only byte/Unicode mapping data.
- Any display ordering, normalization, or higher-level script behavior is outside this module.

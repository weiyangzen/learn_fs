# File Research: sources/os/linux/linux-stable/fs/nls/nls_cp865.c

Implements Linux NLS support for DOS codepage `cp865`, described as Norwegian/Danish. It is built by `CONFIG_NLS_CODEPAGE_865`.

Key contents:
- `charset2uni[256]` maps Nordic DOS bytes, ASCII, drawing characters, and symbols to Unicode.
- Reverse pages are `page00`, `page01`, `page03`, `page20`, `page22`, `page23`, and `page25`.
- Case tables handle ASCII plus Nordic accented/currency-like characters where encoded.
- `uni2char()` emits one byte for exact reverse page hits.
- `char2uni()` decodes one byte and rejects byte `0x00`.
- Registers `.charset = "cp865"`.

Important behavior:
- Supports Norwegian/Danish legacy DOS filename conversion.
- The file is operationally identical to cp437/cp861-style modules except for the generated mapping data.

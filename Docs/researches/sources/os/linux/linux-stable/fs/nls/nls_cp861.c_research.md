# File Research: sources/os/linux/linux-stable/fs/nls/nls_cp861.c

Implements Linux NLS support for DOS codepage `cp861`, described as Icelandic. It is built from `CONFIG_NLS_CODEPAGE_861`.

Key contents:
- `charset2uni[256]` maps cp861 Icelandic Latin characters, ASCII, DOS graphics, and symbols to Unicode.
- Reverse pages are `page00`, `page01`, `page03`, `page20`, `page22`, `page23`, and `page25`.
- `charset2lower` and `charset2upper` include Icelandic-specific case pairs where encoded.
- `uni2char()` and `char2uni()` are the standard generated one-byte NLS conversion functions.
- Registers `.charset = "cp861"` with module description `NLS Codepage 861 (Icelandic)`.

Important behavior:
- Provides exact cp861 conversion only; unsupported Unicode returns `-EINVAL`.
- Suitable for legacy FAT/DOS filename conversion using Icelandic codepage data.

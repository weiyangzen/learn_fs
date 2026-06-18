# File Research: sources/os/linux/linux-stable/fs/nls/nls_cp860.c

Implements Linux NLS support for DOS codepage `cp860`, described as Portuguese. It is built through `CONFIG_NLS_CODEPAGE_860`.

Key contents:
- `charset2uni[256]` maps Portuguese DOS bytes, ASCII, box drawing, Greek/math symbols, and block elements to Unicode.
- Reverse pages are `page00`, `page03`, `page20`, `page22`, `page23`, and `page25`.
- Case folding tables cover ASCII and cp860 accented Latin pairs.
- `uni2char()` checks `boundlen`, indexes `page_uni2charset`, and returns one byte for exact mappings.
- `char2uni()` decodes one byte through `charset2uni`.
- Registers `.charset = "cp860"`.

Important behavior:
- The module is table-driven and has no external dependencies beyond the Linux module/NLS headers.
- It supports cp860 filename conversion for FAT/DOS-style filesystems.

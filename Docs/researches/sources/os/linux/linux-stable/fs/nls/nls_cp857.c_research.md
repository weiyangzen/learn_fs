# File Research: sources/os/linux/linux-stable/fs/nls/nls_cp857.c

Implements Linux NLS support for DOS codepage `cp857`, described as Turkish. It is built by `CONFIG_NLS_CODEPAGE_857`.

Key contents:
- `charset2uni[256]` maps cp857 Turkish/Latin bytes, ASCII, and drawing characters to Unicode.
- Reverse pages are `page00`, `page01`, and `page25`.
- Case conversion tables include Turkish-specific byte mappings where representable in cp857.
- `page_uni2charset` is sparse and only enables exact reverse conversion for those three Unicode high-byte pages.
- `uni2char()` emits a single byte on success; `char2uni()` decodes one byte.
- Registers `.charset = "cp857"`.

Important behavior:
- Used for Turkish DOS/FAT filename handling.
- As with the rest of this group, byte `0x00` is considered invalid by `char2uni()` and Unicode zero does not encode through `uni2char()`.

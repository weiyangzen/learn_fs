# File Research: sources/os/linux/linux/fs/nls/nls_cp1251.c

Implements the `cp1251` Windows Cyrillic NLS codepage module.

Key behavior:
- Provides generated Windows CP1251 mappings for Cyrillic plus punctuation and symbols.
- `charset2uni` maps Cyrillic uppercase/lowercase ranges directly in `0xc0-0xff`, with additional Cyrillic letters in `0x80-0xbf`.
- Reverse lookup uses pages `00`, `04`, `20`, and `21`.
- Case tables encode Cyrillic case conversion as well as ASCII case conversion.
- Registers charset name `cp1251`.

Important interactions:
- The module description names Bulgarian and Belarusian, but the table is the general Windows CP1251 charset.
- Like the other table modules, it performs no best-fit transliteration.

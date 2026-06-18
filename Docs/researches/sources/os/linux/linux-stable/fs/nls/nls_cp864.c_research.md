# File Research: sources/os/linux/linux-stable/fs/nls/nls_cp864.c

Implements Linux NLS support for DOS codepage `cp864`, described as Arabic. It is selected by `CONFIG_NLS_CODEPAGE_864`.

Key contents:
- `charset2uni[256]` maps cp864 Arabic, Latin/symbol, and drawing bytes to Unicode.
- Reverse pages are `page00`, `page03`, `page06`, `page22`, `page25`, and `pagefe`.
- `page06` contains Arabic Unicode reverse mappings; `pagefe` covers Arabic presentation-form mappings used by this codepage.
- Case tables primarily affect ASCII/Latin-compatible bytes; Arabic script itself is caseless.
- `page_uni2charset` is larger in visible sparse form because it must place `pagefe` at high-byte slot `0xfe`.
- `uni2char()` and `char2uni()` follow the standard one-byte generated NLS pattern.
- Registers `.charset = "cp864"`.

Important behavior:
- This module is only charset translation. It does not implement Arabic shaping, joining, bidi ordering, or normalization.
- Reverse mappings are exact, including presentation forms where explicitly listed.

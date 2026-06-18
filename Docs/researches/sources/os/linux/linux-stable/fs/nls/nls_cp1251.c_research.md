# File Research: sources/os/linux/linux-stable/fs/nls/nls_cp1251.c

This file implements the Windows CP1251 NLS module, described for Bulgarian and Belarusian and registered as `cp1251`.

`charset2uni[256]` maps CP1251 bytes to Unicode, with Cyrillic uppercase/lowercase ranges at `0xc0`-`0xff`, Cyrillic extensions in the `0x80` and `0xa0` ranges, and punctuation/symbol mappings such as Euro, quotes, dashes, bullet, trademark, and numero sign. Undefined bytes are encoded as `0x0000`. Reverse lookup is stored in `page00`, `page04`, `page20`, and `page21`.

The case tables are meaningful. `charset2lower` maps ASCII uppercase to lowercase and maps Cyrillic uppercase bytes to their lowercase byte equivalents. `charset2upper` performs the inverse for ASCII and Cyrillic, including special CP1251 Cyrillic letters in the upper control-extension range.

The conversion callbacks are the common NLS generated form. `uni2char()` does sparse reverse lookup and rejects unmappable Unicode values; `char2uni()` maps input bytes and rejects `0x0000` entries. The table exposes these callbacks as `.charset = "cp1251"`.

The module registers through `init_nls_cp1251()`, unregisters through `exit_nls_cp1251()`, and declares `MODULE_DESCRIPTION("NLS Windows CP1251 (Bulgarian, Belarusian)")` with `Dual BSD/GPL` license.

# File Research: sources/os/linux/linux-stable/fs/nls/mac-inuit.c

This file implements the Linux NLS module for Macintosh Inuit, registered as `macinuit`.

The table targets Canadian Aboriginal Syllabics/Inuktitut byte mappings. `charset2uni[256]` maps ASCII/control bytes directly and maps most high bytes into Unicode ranges `0x1400` through `0x1676`, with a few common punctuation/symbol entries such as bullet, paragraph sign, copyright, trademark, en/em dash, quotes, and Polish L-with-stroke entries at `0xfe`/`0xff`. Reverse conversion is sparse across Unicode pages `page00`, `page01`, `page14`, `page15`, `page16`, `page20`, and `page21`.

The conversion functions are the same single-byte NLS pattern used by the other generated tables. `uni2char()` rejects insufficient output space and Unicode code points not present in the reverse page table. `char2uni()` returns the mapped Unicode value for one byte and reports `-EINVAL` for entries mapped to `0x0000`.

A notable difference from most neighboring Mac files is the case table content: `charset2lower` is filled with `0xff`, while `charset2upper` is filled with `0xfe`. These are not useful alphabetic folds for the syllabics repertoire; consumers should treat this module as a charset translator, not a locale-aware case mapper.

The file registers with `register_nls(&table)` in `init_nls_macinuit()` and unregisters in `exit_nls_macinuit()`. Module metadata identifies it as `NLS Codepage macinuit`, with `Dual BSD/GPL` license and the Unicode data permission notice.

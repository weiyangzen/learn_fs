# File Research: sources/os/linux/linux-stable/fs/nls/nls_cp1250.c

This file implements the Windows CP1250 NLS module for Slavic/Central European languages, registered as `cp1250`.

`charset2uni[256]` maps CP1250 bytes to Unicode, preserving ASCII/control values and mapping high bytes to Central European Latin characters, punctuation, currency/symbols, and combining-like spacing diacritics. Undefined CP1250 byte positions are represented by `0x0000`. Reverse conversion uses Unicode pages `page00`, `page01`, `page02`, `page20`, and `page21`.

The file provides meaningful case conversion tables. `charset2lower` and `charset2upper` preserve ASCII case folding and also map Central European uppercase/lowercase byte pairs where representable in CP1250. This makes it more useful for case-insensitive filename handling than the Mac tables in this group.

The conversion callbacks follow the NLS convention: one Unicode code point to one byte in `uni2char()`, one byte to one Unicode code point in `char2uni()`, with `-ENAMETOOLONG` on missing output capacity and `-EINVAL` for unmappable values.

Module lifecycle is standard: `init_nls_cp1250()` registers the table and `exit_nls_cp1250()` unregisters it. Metadata declares `NLS Windows CP1250 (Slavic/Central European Languages)` and `Dual BSD/GPL`.

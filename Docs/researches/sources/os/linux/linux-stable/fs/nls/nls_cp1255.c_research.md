# File Research: sources/os/linux/linux-stable/fs/nls/nls_cp1255.c

This file implements the Windows CP1255 Hebrew NLS module and also exposes alias `iso8859-8`.

`charset2uni[256]` maps CP1255 bytes to Unicode. The high range includes Hebrew points and punctuation (`U+05B0` through `U+05C3`), Hebrew letters (`U+05D0` through `U+05EA`), Yiddish ligature letters (`U+05F0` through `U+05F4`), New Sheqel sign, common Windows punctuation, and undefined slots as `0x0000`. Reverse lookup uses `page00`, `page01`, `page02`, `page05`, `page20`, and `page21`.

The NLS table differs from the other Windows files by declaring `.alias = "iso8859-8"` and `MODULE_ALIAS_NLS(iso8859-8)`, allowing module resolution by either CP1255 or ISO-8859-8 naming even though the table is CP1255-oriented.

The case tables preserve ASCII folding but Hebrew code points themselves have no uppercase/lowercase distinction. Many undefined/nonalphabetic high bytes map to `0x00`, while Hebrew byte ranges are effectively identity-preserved for upper/lower fields.

The conversion callbacks are standard: `uni2char()` maps one Unicode code point to one byte via sparse reverse pages, and `char2uni()` maps one byte to Unicode. Both treat unmapped entries as errors, with `uni2char()` also enforcing output capacity.

Lifecycle is standard registration/unregistration. Metadata declares `NLS Hebrew charsets (ISO-8859-8, CP1255)`, `Dual BSD/GPL`, and the NLS alias.

# File Research: sources/os/linux/linux-stable/fs/nls/mac-iceland.c

This file implements the Linux NLS module for Macintosh Icelandic, registered as charset `maciceland`.

The core data is generated mapping state. `charset2uni[256]` maps Mac Icelandic bytes to Unicode, preserving the lower ASCII range and mapping high bytes to accented Latin characters, Icelandic-specific letters such as eth/thorn, mathematical symbols, punctuation, the Euro sign, and the Apple private-use character `0xf8ff`. Reverse lookup is organized into sparse Unicode page arrays: `page00`, `page01`, `page02`, `page03`, `page20`, `page21`, `page22`, `page25`, and `pagef8`.

The module uses the usual NLS single-byte conversion callbacks:
- `uni2char()` maps Unicode to one output byte through `page_uni2charset`; it fails on zero capacity or unmappable code points.
- `char2uni()` maps one input byte to a `wchar_t`; byte values mapped to `0x0000` are treated as invalid.
- The NLS table binds these callbacks and the static case tables.

The high-byte mapping is close to Mac Roman but swaps in Icelandic coverage: for example `0xdc`/`0xdd`/`0xde`/`0xdf` cover uppercase/lowercase eth and thorn, while the table keeps common Mac symbol mappings like `0xf0 -> 0xf8ff`. `charset2lower` and `charset2upper` are both initialized with `0xff` throughout, so there is no practical case-folding behavior exposed through this table.

The lifecycle functions register and unregister the table with the kernel NLS registry. Metadata declares `NLS Codepage maciceland`, `Dual BSD/GPL`, and includes the Unicode data permission notice.

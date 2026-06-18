# File Research: sources/os/linux/linux-stable/fs/nls/mac-romanian.c

This file implements the Linux NLS module for Macintosh Romanian, registered as `macromanian`.

The file is a generated single-byte charset translation table. `charset2uni[256]` is mostly Mac Roman-like, but it replaces some high-byte entries with Romanian-specific letters: `U+0102/U+0103`, `U+0218/U+0219`, and `U+021A/U+021B` are present in the high range. Reverse conversion uses sparse Unicode page arrays `page00`, `page01`, `page02`, `page03`, `page20`, `page21`, `page22`, `page25`, and `pagef8`.

The conversion mechanics match the other generated NLS modules. `uni2char()` performs a reverse page lookup from Unicode to one byte, bounds-checks output length, and reports unmappable characters. `char2uni()` maps one byte to Unicode and treats `0x0000` table entries as invalid. The exported NLS table supplies these callbacks plus lower/upper tables to the common NLS framework.

The table differs from `mac-roman.c` mainly by Romanian byte assignments and by not carrying the `pagefb` ligature reverse table. The case tables are all `0xff`, so any caller needing case-insensitive matching should not rely on this module for Romanian case folding.

Lifecycle and metadata are standard: `init_nls_macromanian()` registers, `exit_nls_macromanian()` unregisters, and the module is described as `NLS Codepage macromanian` under `Dual BSD/GPL`, with the Unicode data permission notice.

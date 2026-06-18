# File Research: sources/os/linux/linux-stable/fs/nls/nls_iso8859-7.c

Purpose: Generated Linux NLS module for ISO 8859-7, described as Modern Greek.

Core structures and data:
- `charset2uni[256]` maps Greek letters, Greek tonos/dialytika characters, and selected punctuation.
- Reverse maps include `page00`, `page02`, `page03`, and `page20`.
- Case tables map Greek uppercase/lowercase byte values and preserve nonletters.

Important behavior:
- `uni2char()` emits one byte for exactly represented Unicode code points and rejects unmapped inputs.
- `char2uni()` maps one byte to Unicode and rejects zero-valued table entries.
- The registered charset name is `"iso8859-7"`.

Dependencies and interfaces:
- Standard generated NLS implementation.

Design notes and risks:
- The file includes sparse reverse mappings for modifier letters and U+2015, so not all Greek-related Unicode input is accepted.
- Some Greek code points are undefined in the byte table; byte-to-Unicode can fail on those byte positions.

# File Research: sources/os/linux/linux-stable/fs/nls/nls_iso8859-6.c

Purpose: Generated Linux NLS module for ISO 8859-6, described as Arabic.

Core structures and data:
- `charset2uni[256]` maps Arabic punctuation, letters, and Arabic-Indic digits. Notably byte `0x30` through `0x39` map to U+0660 through U+0669 rather than ASCII digits.
- Reverse maps include `page00` and `page06`.
- Case conversion tables are mostly identity or zero because Arabic has no upper/lowercase distinction in this charset.

Important behavior:
- `uni2char()` exact-maps Unicode page 0 and 6 characters to one byte.
- `char2uni()` rejects undefined slots and NUL.
- The registered charset name is `"iso8859-6"`.

Dependencies and interfaces:
- Self-contained generated NLS table.

Design notes and risks:
- The ASCII digit byte range is intentionally mapped to Arabic-Indic Unicode digits by the table; consumers expecting ASCII digits from bytes `0x30`-`0x39` would be surprised.
- Many high-byte positions are undefined and return `-EINVAL`.

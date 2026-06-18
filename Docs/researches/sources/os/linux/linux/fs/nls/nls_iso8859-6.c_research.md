# File Research: sources/os/linux/linux/fs/nls/nls_iso8859-6.c

Purpose: Generated Linux NLS module for ISO 8859-6, described as Arabic.

Core structures and data:
- `charset2uni[256]` maps Arabic punctuation, letters, and Arabic-Indic digits.
- Byte `0x30` through `0x39` map to U+0660 through U+0669, not ASCII digits.
- Reverse mappings include `page00` and `page06`.
- Case tables are mostly identity or zero because this charset has no upper/lowercase distinction.

Important behavior:
- `uni2char()` exact-maps Unicode page 0 and page 6 values to one byte.
- `char2uni()` rejects undefined slots and NUL.
- Registers charset `"iso8859-6"`.

Dependencies and interfaces:
- Self-contained generated NLS table.

Design notes and risks:
- The digit mapping is surprising for code expecting ASCII digit Unicode from byte `0x30`.
- Many high-byte positions are undefined and return `-EINVAL`.

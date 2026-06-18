# File Research: sources/os/linux/linux/fs/nls/nls_iso8859-7.c

Purpose: Generated Linux NLS module for ISO 8859-7, described as Modern Greek.

Core structures and data:
- `charset2uni[256]` maps Greek letters, tonos/dialytika characters, and selected punctuation.
- Reverse maps include `page00`, `page02`, `page03`, and `page20`.
- Case tables map Greek uppercase/lowercase byte values.

Important behavior:
- `uni2char()` emits one byte for exactly represented Unicode code points.
- `char2uni()` maps one byte and rejects zero-valued entries.
- Registers charset `"iso8859-7"`.

Dependencies and interfaces:
- Standard generated NLS implementation.

Design notes and risks:
- Sparse reverse mappings cover modifier letters and U+2015.
- Some Greek byte positions are undefined and fail byte-to-Unicode conversion.

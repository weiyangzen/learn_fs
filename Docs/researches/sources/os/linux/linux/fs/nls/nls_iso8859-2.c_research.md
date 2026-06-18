# File Research: sources/os/linux/linux/fs/nls/nls_iso8859-2.c

Purpose: Generated Linux NLS module for ISO 8859-2 / Latin-2, described as Slavic/Central European Languages.

Core structures and data:
- `charset2uni[256]` maps Central European Latin extended letters and diacritics.
- Reverse maps include `page00`, `page01`, and `page02`.
- Case tables encode charset-specific upper/lower pairs.

Important behavior:
- `uni2char()` performs exact reverse lookup and returns one byte or an errno.
- `char2uni()` consumes one byte and rejects zero-valued mappings.
- Registers charset `"iso8859-2"`.

Dependencies and interfaces:
- Self-contained generated NLS table.
- Module init/exit only register and unregister the table.

Design notes and risks:
- Reverse table value `0xff` is valid for U+02D9; only `0x00` is the unmapped sentinel.
- The generated helper cannot encode Unicode NUL.

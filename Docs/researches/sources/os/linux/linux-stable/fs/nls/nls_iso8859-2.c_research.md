# File Research: sources/os/linux/linux-stable/fs/nls/nls_iso8859-2.c

Purpose: Generated Linux NLS module for ISO 8859-2 / Latin-2, described as Slavic/Central European Languages.

Core structures and data:
- `charset2uni[256]` maps bytes to Latin Extended-A letters and diacritics used by Central European languages.
- Reverse maps include `page00`, `page01`, and `page02`, because exact mappings include spacing diacritics in Unicode page 2.
- `charset2lower` and `charset2upper` encode the charset-specific case pairs.

Important behavior:
- `uni2char()` performs exact page lookup and returns one output byte or an errno.
- `char2uni()` consumes one byte and rejects zero-valued mappings.
- The registered charset name is `"iso8859-2"`.

Dependencies and interfaces:
- Self-contained NLS table module using generated lookup arrays.
- Module init/exit only register and unregister the table.

Design notes and risks:
- Reverse mapping includes `0xff` for U+02D9, showing that the lookup arrays may use byte `0xff` as a valid result, while `0x00` is the unmapped sentinel.
- The common conversion helper cannot encode Unicode NUL.

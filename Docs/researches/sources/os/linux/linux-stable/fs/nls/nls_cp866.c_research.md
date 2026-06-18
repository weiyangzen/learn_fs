# File Research: sources/os/linux/linux-stable/fs/nls/nls_cp866.c

Implements Linux NLS support for DOS codepage `cp866`, described as Cyrillic/Russian. It is selected by `CONFIG_NLS_CODEPAGE_866`.

Key contents:
- `charset2uni[256]` maps cp866 Cyrillic/Russian bytes plus ASCII and DOS graphic symbols to Unicode.
- Reverse pages are `page00`, `page04`, `page21`, `page22`, and `page25`.
- `page04` holds Cyrillic reverse mappings; `page21`/`page22`/`page25` handle selected symbols and drawing characters.
- Case conversion tables provide Cyrillic and ASCII upper/lower mappings in cp866 byte space.
- `uni2char()` and `char2uni()` are standard one-byte conversion functions.
- Registers `.charset = "cp866"`.

Important behavior:
- This is the common Russian DOS codepage path for Linux filesystem name conversion.
- Conversion failure is explicit: unsupported Unicode returns `-EINVAL`, not a replacement byte.

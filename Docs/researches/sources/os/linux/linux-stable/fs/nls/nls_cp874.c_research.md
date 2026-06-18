# File Research: sources/os/linux/linux-stable/fs/nls/nls_cp874.c

Implements Linux NLS support for Thai `cp874` / TIS-620, described as `NLS Thai charset (CP874, TIS-620)`. It is built by `CONFIG_NLS_CODEPAGE_874`.

Key contents:
- `charset2uni[256]` maps ASCII, Thai characters, and selected punctuation/symbol bytes to Unicode.
- Reverse pages are `page00`, `page0e`, and `page20`.
- `page0e` contains Thai Unicode reverse mappings.
- Case tables are mostly identity/ASCII-oriented because Thai script has no case.
- The table registers `.charset = "cp874"` and `.alias = "tis-620"`, unlike most neighboring modules which only set `.charset`.
- `uni2char()` and `char2uni()` follow the same single-byte exact conversion and NUL rejection pattern.

Important behavior:
- Supports both the cp874 charset name and TIS-620 alias for NLS loading.
- No Thai segmentation, shaping, or normalization is performed; this is only byte-to-Unicode mapping for filesystem strings.

# File Research: sources/os/linux/linux/fs/nls/nls_koi8-u.c

Purpose: Generated Linux NLS module for KOI8-U, described as Ukrainian.

Core structures and data:
- `charset2uni[256]` maps ASCII, graphics characters, Cyrillic letters, and Ukrainian-specific letters.
- Reverse maps include `page00`, `page04`, `page22`, `page23`, and `page25`.
- `charset2lower` and `charset2upper` implement KOI8-U byte-level case conversion.

Important behavior:
- `uni2char()` exact-maps Unicode through sparse reverse pages.
- `char2uni()` consumes one byte for nonzero mappings and rejects zero entries.
- Registers charset `"koi8-u"`.

Dependencies and interfaces:
- Self-contained NLS module.
- Serves as the runtime backend for `nls_koi8-ru.c`.

Design notes and risks:
- Supports line/box drawing and mathematical symbols in addition to Cyrillic.
- Differences from KOI8-R are concentrated around Ukrainian-specific Cyrillic and upper-byte graphics slots.

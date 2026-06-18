# File Research: sources/os/linux/linux-stable/fs/nls/nls_koi8-u.c

Purpose: Generated Linux NLS module for KOI8-U, described as Ukrainian.

Core structures and data:
- `charset2uni[256]` maps ASCII, graphics characters, Cyrillic letters, and Ukrainian-specific letters such as Ukrainian Ye, I, Yi, and Ghe with upturn.
- Reverse maps include `page00`, `page04`, `page22`, `page23`, and `page25`.
- `charset2lower` and `charset2upper` implement KOI8-U byte-level case conversion.

Important behavior:
- `uni2char()` exact-maps Unicode code points through sparse reverse page tables.
- `char2uni()` returns one consumed byte for nonzero mappings and rejects zero entries.
- The registered charset name is `"koi8-u"`.

Dependencies and interfaces:
- Self-contained NLS table module; also serves as the runtime backend for `nls_koi8-ru.c`.

Design notes and risks:
- Like KOI8-R, it supports line/box drawing characters and mathematical symbols in addition to Cyrillic letters.
- Differences from KOI8-R are concentrated in the upper byte table around Ukrainian-specific Cyrillic and some graphics slots.

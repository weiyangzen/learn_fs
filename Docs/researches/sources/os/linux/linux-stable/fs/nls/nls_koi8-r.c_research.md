# File Research: sources/os/linux/linux-stable/fs/nls/nls_koi8-r.c

Purpose: Generated Linux NLS module for KOI8-R, described as Russian.

Core structures and data:
- `charset2uni[256]` maps ASCII, box drawing symbols, mathematical symbols, and Cyrillic letters.
- Reverse maps include `page00`, `page04`, `page22`, `page23`, and `page25`.
- Case tables provide KOI8-R byte-level Cyrillic casing and identity handling for graphics characters.

Important behavior:
- `uni2char()` performs exact Unicode-to-KOI8-R lookup and emits one byte.
- `char2uni()` maps one byte to Unicode and rejects zero-valued entries.
- The registered charset name is `"koi8-r"`.

Dependencies and interfaces:
- Self-contained generated NLS table.

Design notes and risks:
- KOI8-R includes many line drawing and block characters, which explains the larger reverse page coverage compared with ISO 8859 files.
- It uses the same zero sentinel pattern; Unicode NUL and unmapped graphics/code points are rejected.

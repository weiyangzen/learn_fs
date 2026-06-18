# File Research: sources/os/linux/linux/fs/nls/nls_koi8-r.c

Purpose: Generated Linux NLS module for KOI8-R, described as Russian.

Core structures and data:
- `charset2uni[256]` maps ASCII, box drawing, mathematical symbols, and Cyrillic letters.
- Reverse maps include `page00`, `page04`, `page22`, `page23`, and `page25`.
- Case tables provide KOI8-R byte-level Cyrillic casing and identity handling for graphics characters.

Important behavior:
- `uni2char()` performs exact Unicode-to-KOI8-R lookup.
- `char2uni()` maps one byte and rejects zero-valued entries.
- Registers charset `"koi8-r"`.

Dependencies and interfaces:
- Self-contained generated NLS table.

Design notes and risks:
- KOI8-R’s graphics characters explain the broader reverse page coverage.
- Unicode NUL and unmapped code points are rejected by the zero-sentinel convention.

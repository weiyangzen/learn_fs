# File Research: sources/os/linux/linux-stable/fs/nls/nls_iso8859-4.c

Purpose: Generated Linux NLS module for ISO 8859-4 / Latin-4, described as old Baltic charset.

Core structures and data:
- `charset2uni[256]` covers Baltic and Nordic Latin extended letters.
- Reverse maps include `page00`, `page01`, and `page02`.
- `charset2lower` and `charset2upper` provide one-byte case transforms for the charset.

Important behavior:
- `uni2char()` maps exact Unicode code points back to one byte using `page_uni2charset`.
- `char2uni()` returns one-byte consumption for mapped entries and `-EINVAL` for zero mappings.
- The registered charset name is `"iso8859-4"`.

Dependencies and interfaces:
- Self-contained NLS table, no runtime-loaded backend.

Design notes and risks:
- Like ISO 8859-2, some reverse mappings for spacing diacritics live on Unicode page 2.
- The file has generated-table complexity only; no multibyte parsing or stateful conversion exists.

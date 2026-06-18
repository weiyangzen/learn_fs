# File Research: sources/os/linux/linux/fs/nls/nls_iso8859-4.c

Purpose: Generated Linux NLS module for ISO 8859-4 / Latin-4, described as old Baltic charset.

Core structures and data:
- `charset2uni[256]` covers Baltic and Nordic Latin extended letters.
- Reverse mappings include `page00`, `page01`, and `page02`.
- `charset2lower` and `charset2upper` provide byte-level case conversion.

Important behavior:
- `uni2char()` maps exact Unicode code points back to one byte.
- `char2uni()` returns one-byte consumption for mapped entries and `-EINVAL` for zero mappings.
- Registers charset `"iso8859-4"`.

Dependencies and interfaces:
- Self-contained generated NLS table.
- No runtime-loaded backend.

Design notes and risks:
- Some spacing diacritics live on Unicode page 2.
- There is no multibyte parsing or stateful conversion.

# File Research: sources/virtualization/nbdkit/plugins/data/disk2data.pl

Perl utility that converts a disk image into an `nbdkit data data="..." size=N` command line.

Key behavior:
- Requires one disk image argument and opens it raw.
- Scans the file byte-by-byte, skipping long zero ranges by emitting `@0xOFFSET`.
- Emits short zero gaps directly when cheaper than an offset directive.
- Detects repeated short-period patterns up to period 8 and emits `BYTE*N` or `(pattern)*N`.
- Emits non-zero byte runs as decimal byte values.
- Always prints `size=<actual file size>`.

Use case:
- Helpful for compactly describing small or sparse disk images in the data plugin’s mini-language.
- Not suitable for large fully populated images due to command-line size limits.

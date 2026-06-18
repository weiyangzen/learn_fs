# File Research: sources/os/plan9/9front/sys/src/cmd/scat/prose.c

Purpose: Expands compact catalog description strings into readable prose.

Key routines:
- `append`, `matchlen`: local string helpers.
- `prose`: walks an encoded description, translates known abbreviations through a descriptor table, handles punctuation, Messier tags, star-count shorthand, and magnitude notation.
- `prdesc`: lazily builds first-character indexes into the descriptor table and prints expanded prose plus original bracketed text.

Integration: Used by `scat.c` for NGC record descriptions, with `desctab` from `desc.c`.

Risks:
- Uses a static 512-byte output buffer and aborts if exceeded.
- Descriptor table must be sorted/grouped by first character for index lookup.

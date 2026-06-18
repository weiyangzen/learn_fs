# File Research: sources/local-fs/xfsprogs/db/text.c

Implements raw text/hex display for current `xfs_db` buffers.

Key responsibilities:
- `print_text` dumps the current IO buffer.
- Formats offsets, hex bytes, and printable alphanumeric characters in 16-byte rows.
- Replaces non-alphanumeric bytes with `.`.

Dependencies:
- Uses `iocur_top`, `dbprintf`, and libc `isalnum`.

Notable risks:
- The ASCII side only shows `isalnum` characters, so punctuation and whitespace are hidden even if printable.
- `dbprintf(".", *s)` passes an unused argument, harmless but imprecise.

# File Research: sources/local-fs/linux-apfs-rw/unicode.h

This header declares the APFS Unicode normalization cursor interface used by filename/key handling code.

Exports:
- `struct apfs_unicursor` stores the current UTF-8 pointer, remaining total byte length, normalized segment length, last emitted normalized position, and last canonical combining class.
- `apfs_init_unicursor()` initializes the cursor over a UTF-8 string.
- `apfs_normalize_next()` advances the cursor and returns one normalized UTF-32 codepoint, optionally case folded.

Dependencies:
- Includes `<linux/nls.h>` for `unicode_t`.
- Consumed by `unicode.c`, with call sites in `namei.c` and `key.c`.

Design notes:
- The cursor exposes enough state for `unicode.c` to reorder combining marks without allocating a normalized string.
- Callers should treat return value `0` as end or invalid normalization, matching the implementation’s sentinel behavior.

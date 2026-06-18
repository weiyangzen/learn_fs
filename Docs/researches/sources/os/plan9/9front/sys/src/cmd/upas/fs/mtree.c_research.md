# File Research: sources/os/plan9/9front/sys/src/cmd/upas/fs/mtree.c

This file maintains a digest-indexed AVL tree of top-level messages.

Key behavior:
- `mtreeinit` creates the AVL tree using SHA1 digest comparison.
- `mtreefind` looks up a message by digest.
- `mtreeadd` inserts a message and returns an existing duplicate if present.
- `mtreedelete` removes a message, with special handling for messages already marked deleted/dead.
- Uses pointer arithmetic through `messageof` because `Message` embeds the digest field at the same offset as `Mtree.digest`.

Integration and risks:
- Used for duplicate detection and index merge in `cache.c`/`idx.c`.
- Depends on `Message` layout embedding `Idx`/`Mtree`-compatible fields.

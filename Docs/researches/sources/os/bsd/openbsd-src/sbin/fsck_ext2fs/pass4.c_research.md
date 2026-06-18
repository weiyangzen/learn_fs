# File Research: sources/os/bsd/openbsd-src/sbin/fsck_ext2fs/pass4.c

Implements ext2 fsck phase 4: reference count and unresolved inode cleanup.

Top-level behavior:
- Iterates allocated inodes through `lastino`.
- For regular files and connected directories, adjusts nonzero remaining link-count deltas or clears zero-link inodes tracked in `zlnhead`.
- Clears unreferenced directories still in `DSTATE`.
- Clears zero-length directories marked `DCLEAR`.
- Clears bad/duplicate files and directories marked `FCLEAR` or `DCLEAR`.

`pass4check` is the block-release callback:
- Skips out-of-range blocks.
- For allocated blocks, removes duplicate-list records when present.
- If a block is not still duplicated, clears it from the block map and decrements used block count.

This pass reconciles inode link counts and releases blocks from inodes that earlier phases decided cannot remain allocated.

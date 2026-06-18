# File Research: sources/local-fs/xfsdump/restore/inomap.h

## Summary
Defines restore inode-map states, the persistent segment/hunk layout, and the public restore-side inode-map API.

## Main Contents
- `MAP_INO_UNUSED`, directory/non-directory changed and unchanged states, subtree-support state, and `MAP_NDR_NOREST`.
- `seg_t`, representing 64 inodes starting at `base` with three 64-bit bitmaps.
- `hnk_t`, a 4-page chunk containing many segments, a `maxino`, and a transient linked-list pointer.
- `INOPERSEG`, `HNKSZ`, and `SEGPERHNK` sizing macros.
- APIs to restore, sync, delete, sanitize, query, mutate, discard, and iterate inode maps.

## Risks
The persistent layout is ABI-sensitive because map hunks are serialized on dump media and stored in housekeeping files.

`hnk_t` includes a pointer that must be reconstructed after mmap; persisted pointer values are intentionally not portable.

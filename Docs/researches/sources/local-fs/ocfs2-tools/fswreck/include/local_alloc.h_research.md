# File Research: sources/local-fs/ocfs2-tools/fswreck/include/local_alloc.h

This header declares local allocation inode corruption helpers.

Exports:
- Empty local alloc metadata corruption.
- Local alloc bitmap corruption.
- Local alloc used-count corruption.

Integration notes:
- Implemented in `local_alloc.c`.
- Used by `corrupt_local_alloc()`.

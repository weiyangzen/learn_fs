# File Research: sources/local-fs/xfsprogs/repair/rt.h

Header for realtime repair helpers.

Exports:
- Realtime bitmap/summary generation and validation: `generate_rtinfo`, `check_rtbitmap`, `check_rtsummary`, `fill_rtbitmap`, `fill_rtsummary`.
- Rtgroup metadata inode lifecycle: `discover_rtgroup_inodes`, `unload_rtgroup_inodes`, `init_rtgroup_inodes`, `free_rtgroup_inodes`.
- Metadata inode classification: `is_rtgroup_inode` plus inline wrappers for bitmap, summary, rmap, and refcount inode types.
- Corruption tracking: `mark_rtgroup_inodes_bad`, `rtgroup_inodes_were_bad`.
- Realtime superblock operations: `check_rtsb`, `rewrite_rtsb`.

The header is consumed by repair phases and rmap/refcount code that need to avoid or rebuild rtgroup metadata.

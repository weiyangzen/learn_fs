# File Research: sources/local-fs/ocfs2-tools/fswreck/include/fsck_type.h

This header defines the fswreck corruption code namespace.

Key content:
- `enum fsck_type` enumerates corruption IDs from `EB_BLKNO` through `INODE_VALID_FLAG`, ending at `NUM_FSCK_TYPE`.
- The enum mirrors `fsck.ocfs2` prompt codes so fswreck can create test cases for fsck repairs.
- Covers extent blocks/lists/records, chain metadata, superblock clusters, group descriptors, discontiguous block groups, inode fields, local alloc, truncate logs, symlinks, directories, inline data, duplicate clusters, journals, quotas, refcounts, metadata ECC, and inode valid flag.
- Long comment groups enum values into conceptual categories and notes unimplemented historical local alloc codes.

Integration notes:
- `main.c` uses enum values as direct indexes into `prompt_codes[]` and `corrupt[]`.
- Any insertion or reorder must be synchronized with prompt table definitions and fsck prompt-code expectations.

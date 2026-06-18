# File Research: sources/local-fs/ocfs2-tools/fsck.ocfs2/pass5.c

Purpose: implements fsck pass 5, validating global quota files enough to preserve quota limits, recomputing quota usage from the repaired filesystem, and recreating global/local quota files.

Read coverage: complete file read, 541 lines.

Key responsibilities:
- Checks whether user and/or group quota ro-compat features are enabled.
- Initializes quota info for each enabled quota type and reads global quota metadata.
- Validates quota header magic/version, quota file block counts, free block references, free entry references, and metadata ECC.
- Recursively scans quota tree blocks and leaf data blocks, ignoring invalid or duplicate references.
- Extracts quota limits into quota hash tables, prompting on duplicate or corrupted quota structures.
- Resets current inode/space usage fields before recomputing actual usage.
- Runs `ocfs2_compute_quota_usage()` and, if writable, truncates and recreates quota files with rebuilt usage and preserved limits.
- Initializes local quota files after rebuilding global quota files.

Important entry points:
- `o2fsck_pass5()` is the pass driver.
- `load_quota_file()` initializes quota info, allocates quota block bitmap, and scans the quota tree.
- `o2fsck_check_info()` validates quota info block and sets default grace/sync values if needed.
- `o2fsck_check_tree_blk()` recursively walks quota tree references.
- `o2fsck_check_data_blk()` validates and imports quota entries.
- `recreate_quota_files()` truncates and rebuilds quota files.
- `truncate_cached_inode()` zeros/truncates cached quota inode data.

Dependencies:
- Uses libocfs2 quota hash, quota file, quota format swap, file read, ECC, quota usage computation, truncate, and initialization APIs.
- Uses `qbmp` bitmaps to avoid rescanning quota blocks and `qhash` to preserve per-id quota limits.

Risk and edge cases:
- Node-local quota files are not checked for limits; comments state they are discarded/reinitialized.
- Corrupt quota metadata can still be scanned if the user chooses to trust referenced content.
- Quota file block counts are capped at 32-bit maximum when copied into quota info.
- On errors, cleanup iterates quota hashes and releases cached dquots.

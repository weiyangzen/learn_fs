# File Research: sources/local-fs/xfsprogs/repair/quotacheck.c

## Role

`quotacheck.c` verifies that quota files match the live inode/block accounting observed by xfs_repair. It builds in-core dquot counters during phase 7 and compares them against on-disk dquot records.

## Core Behavior

- `quotacheck_setup()` decides which quota types to check based on quota flags, discovered quota inodes, lost quota state, and `quotacheck_skip()`.
- `quotacheck_adjust()` opens each live non-quota inode, skips metadata directory files, counts data/realtime blocks, and increments user/group/project quota counters.
- `quotacheck_verify()` opens the quota inode, walks its data extents, reads dquot clusters, compares on-disk counters and types to in-core counts, and reports missing on-disk records.
- `quotacheck_results()` returns checked quota flags, or zero if any mismatch/runtime error cleared the state.
- `discover_quota_inodes()` finds quota metadata inodes from the metadata directory before inode scanning.
- `update_sb_quotinos()` synchronizes superblock quota inode numbers from repair’s discovered state.

## Data Model

Each quota type has a `qc_dquots` AVL64 tree keyed by dquot id. `qc_rec` tracks block count, realtime block count, inode count, and whether a corresponding on-disk record was seen.

## Dependencies

This file uses libxfs quota/dquot/inode/bmap/buffer APIs, repair quota inode tracking globals, AVL64 helpers, and repair logging.

## Risk Areas

- Any allocation, read, extent, or mismatch error clears `chkd_flags`, causing repair not to preserve quota checked flags.
- Realtime block counting requires reading file extents and subtracting realtime blocks from ordinary block counts.
- V4 group/project quota type handling has special root-dquot tolerance because old filesystems can reuse the non-user quota file.

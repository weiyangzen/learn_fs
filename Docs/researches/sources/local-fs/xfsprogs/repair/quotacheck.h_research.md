# File Research: sources/local-fs/xfsprogs/repair/quotacheck.h

## Role

`quotacheck.h` declares quota verification and quota inode discovery/update hooks for xfs_repair.

## Interface

- `quotacheck_skip()` disables quota checking.
- `quotacheck_setup()`, `quotacheck_adjust()`, `quotacheck_verify()`, `quotacheck_results()`, and `quotacheck_teardown()` manage the quota check lifecycle.
- `update_sb_quotinos()` updates superblock quota inode fields.
- `discover_quota_inodes()` finds quota metadata inodes before scanning.

## Dependencies

It references XFS mount, buffer, inode number, and quota type types from libxfs.

## Risk Areas

The lifecycle is split across phases: setup/adjust/verify happen in phase 7, while discovery and superblock update are used earlier/later by repair orchestration.

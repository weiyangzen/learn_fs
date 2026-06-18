# File Research: sources/local-fs/xfsprogs/libxfs/xfs_attr_remote.h

## Purpose

`xfs_attr_remote.h` declares the public libxfs helpers for remote extended attribute values.

## Key Contents

It exposes remote block-count calculation, a max-remote-block helper for the 64 KiB xattr size limit, value get/set helpers, stale/invalidate/remove routines, hole finding, delayed allocation setup, and per-step allocation for deferred attr intents.

## Dependencies and Risks

The declarations tie together `xfs_da_args`, `xfs_attr_intent`, inode bmap records, and buffer invalidation flags. Callers are responsible for preserving `rmtblkno`, `rmtblkcnt`, and `rmtvaluelen` consistently across delayed operation transaction rolls.

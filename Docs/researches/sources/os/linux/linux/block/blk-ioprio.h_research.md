# File Research: sources/os/linux/linux/block/blk-ioprio.h

## Summary
Declares the block cgroup I/O priority hook used to apply cgroup priority policy to bios.

## Main Contents
- Forward declarations for `struct request_queue` and `struct bio`.
- `blkcg_set_ioprio(struct bio *bio)` declaration when `CONFIG_BLK_CGROUP_IOPRIO` is enabled.
- No-op inline fallback when the feature is disabled.

## Important Behavior
The header lets block submission code call `blkcg_set_ioprio()` unconditionally while compiling out all behavior when cgroup I/O priority support is not configured.

## Risks
The fallback silently does nothing, so callers must not rely on priority modification unless the config option is enabled.

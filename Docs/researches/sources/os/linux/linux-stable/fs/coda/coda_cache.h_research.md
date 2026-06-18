# File Research: sources/os/linux/linux-stable/fs/coda/coda_cache.h

## Purpose
Declares Coda minicache APIs for permission caching and invalidation.

## Main Contents
- Permission cache prototypes:
  - `coda_cache_enter()`
  - `coda_cache_clear_inode()`
  - `coda_cache_clear_all()`
  - `coda_cache_check()`
- Child invalidation prototype:
  - `coda_flag_inode_children()`

## Integration Points
Included by Coda directory, cache, and downcall code that checks permissions or marks cached inode/dentry state stale.

## Risks And Review Focus
- Minimal header; changes should stay aligned with `cache.c` and `dir.c` permission/invalidation callers.

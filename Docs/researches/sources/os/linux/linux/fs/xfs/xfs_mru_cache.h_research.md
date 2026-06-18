# File Research: sources/os/linux/linux/fs/xfs/xfs_mru_cache.h

## Purpose

`xfs_mru_cache.h` declares the XFS MRU cache interface and the element structure embedded by clients.

## Main Definitions

- `struct xfs_mru_cache`: opaque cache handle.
- `struct xfs_mru_cache_elem`: list node plus key stored by each cached element.
- `xfs_mru_cache_free_func_t`: client callback used to free expired or failed elements.

## Public API

- global lifecycle: `xfs_mru_cache_init`, `xfs_mru_cache_uninit`
- cache lifecycle: `xfs_mru_cache_create`, `xfs_mru_cache_destroy`
- element operations: `xfs_mru_cache_insert`, `xfs_mru_cache_remove`, `xfs_mru_cache_delete`, `xfs_mru_cache_lookup`, `xfs_mru_cache_done`

## Usage Notes

Clients provide the lifetime, bucket count, opaque data pointer, and free callback at creation time. Successful lookup requires a matching `xfs_mru_cache_done` call to release the cache lock.

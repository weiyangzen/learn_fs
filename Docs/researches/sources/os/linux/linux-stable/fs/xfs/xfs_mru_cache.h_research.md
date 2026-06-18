# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_mru_cache.h

## Purpose
Declares the XFS MRU cache interface and cache element header.

## Main Contents
Defines `struct xfs_mru_cache_elem` with a list node and unsigned long key, plus `xfs_mru_cache_free_func_t` for client cleanup callbacks. Declares global initialization, cache create/destroy, insert/remove/delete, lookup, and lookup completion APIs.

## Usage Contract
Callers embed or allocate an `xfs_mru_cache_elem` for each cached object. Successful lookups keep the internal spinlock held until `xfs_mru_cache_done` is called.

# sources/storage-engines/wiredtiger/src/block_cache/block_map.c

## Purpose

`block_map.c` provides memory-mapped read support for read-only block handles. It maps an underlying file when allowed, unmaps it, and services address-cookie reads directly from the mapped region with optional preload.

## Important APIs, Types, and Functions

The file exports `__wti_blkcache_map`, `__wti_blkcache_unmap`, and `__wti_blkcache_map_read`. It uses `WT_BM.map`, `maplen`, `mapped_cookie`, `WT_BLOCK.verify`, `WT_BLOCK.os_cache_max`, `WT_FILE_HANDLE.fh_map`, `fh_unmap`, and `fh_map_preload`.

## Control Flow

Mapping returns no-op success unless connection mmap is enabled, verify is not active, OS cache limits are not configured, and the file handle supports `fh_map`. Unsupported or busy mapping failures are treated as cache-read fallback. Map reads check that the current `WT_BM` is mapped, assert it is not multi-handle or remote, unpack the address cookie, assert object ID matches the single block handle, and if the requested range lies within the map and preloading succeeds, point the caller buffer at mapped bytes.

## State and Persistence Behavior

This file does not change durable state. It stores mapped-region pointers and cookies in `WT_BM` and can return buffers that alias the mapped file instead of owned memory. It increments mapped-read statistics when successful.

## Dependencies and Integration Points

`block_mgr.c` invokes mapping when loading read-only checkpoints. `block_io.c` tries map reads before block-cache or disk reads. The file depends on file-system mapping hooks and address-cookie unpacking from the file-backed block manager.

## Risks and Edge Cases

Mapping is disabled during verify because mapped reads skip checksum validation. It is disabled when `os_cache_max` is configured because cache usage cannot be controlled. Multi-handle tiered and remote objects are unsupported. Callers must treat mapped buffers as borrowed memory tied to the mapped handle lifetime.

## Test Signals

Signals include successful checkpoint mapping, fallback when mmap is disabled or `fh_map` returns `ENOTSUP`/`EBUSY`, verify disabling mapped reads, object-ID assertions for non-tiered handles, and `block_map_read`/`block_byte_map_read` stats.

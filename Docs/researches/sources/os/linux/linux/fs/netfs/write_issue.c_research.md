# File Research: sources/os/linux/linux/fs/netfs/write_issue.c

High-level writeback and write-through issuing engine for netfs.

Key responsibilities:
- Creates write requests with upload and cache streams.
- Converts dirty folios into write subrequests.
- Handles normal writeback, write-through writes, copy-to-cache writes, and monolithic single-object writeback.
- Drives rolling-buffer iterator advancement.
- Issues subrequests when size/segment limits, discontinuities, EOF, or stream changes require flushing.

Important exported APIs:
- `netfs_prepare_write_failed()`.
- `netfs_writepages()`.
- `netfs_begin_writethrough()`.
- `netfs_advance_writethrough()`.
- `netfs_end_writethrough()`.
- `netfs_writeback_single()`.

Important internal APIs:
- `netfs_create_write_req()`.
- `netfs_prepare_write()`.
- `netfs_reissue_write()`.
- `netfs_issue_write()`.
- `netfs_advance_write()`.

Important behavior:
- `netfs_create_write_req()` initializes stream 0 for server upload and stream 1 for cache write if cache resources are valid.
- `netfs_write_folio()` handles EOF truncation/zeroing, streaming write dirty ranges, writeback groups, cache-copy-only folios, and multi-stream submission ordering.
- `netfs_writepages()` serializes with `ictx->wb_lock`; `WB_SYNC_NONE` can skip on lock contention.
- Unrecoverable startup failure kills dirty pages to avoid endless dirty state.
- Write-through holds `wb_lock` across the operation and can return `-EIOCBQUEUED` for async completion.
- Single-object writeback requires an `ITER_FOLIOQ` iterator and writes all folios as one logical object.

Design note:
- The file documents the core netfs write model: multiple parallel streams overlay a sequence of variable-sized folios.

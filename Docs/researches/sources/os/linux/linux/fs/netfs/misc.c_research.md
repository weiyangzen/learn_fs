# File Research: sources/os/linux/linux/fs/netfs/misc.c

Miscellaneous netfs helper routines for folio queues, dirty/release handling, iterator reset, and request waiting.

Important exported APIs:
- `netfs_alloc_folioq_buffer()`.
- `netfs_free_folioq_buffer()`.
- `netfs_dirty_folio()`.
- `netfs_unpin_writeback()`.
- `netfs_clear_inode_writeback()`.
- `netfs_invalidate_folio()`.
- `netfs_release_folio()`.

Important internal APIs:
- `netfs_reset_iter()`.
- `netfs_wake_collector()`.
- `netfs_subreq_clear_in_progress()`.
- `netfs_wait_for_in_progress_stream()`.
- `netfs_wait_for_read()`.
- `netfs_wait_for_write()`.
- `netfs_wait_for_paused_read()`.
- `netfs_wait_for_paused_write()`.

Important behavior:
- Dirtying a folio can pin the FS-Cache cookie for later writeback using inode state `I_PINNING_NETFS_WB`.
- Invalidate/release paths update zero-point metadata and handle private netfs folio state.
- Collectors may run in the application thread or on a workqueue depending on `NETFS_RREQ_OFFLOAD_COLLECTION`.
- Wait helpers collect progress opportunistically before sleeping.
- Completed reads/writes return transferred length unless failure or unexpected short transfer requires an error.

Dependencies:
- Request collectors from `read_collect.c` and `write_collect.c`.
- Folio queue allocation from `rolling_buffer.c`.
- FS-Cache cookie pin/unpin APIs.

# File Research: sources/os/linux/linux-stable/fs/netfs/misc.c

Miscellaneous netfs helpers for folio queues, dirty/writeback pinning, invalidation, release, waiting, and collector wakeups.

Key behavior:
- Allocates/free folio_queue-backed buffers and marked folios.
- `netfs_reset_iter()` rewinds/truncates a subrequest iterator to remaining bytes.
- `netfs_dirty_folio()` marks a folio dirty and pins the FS-Cache cookie for later writeback.
- `netfs_unpin_writeback()` and `netfs_clear_inode_writeback()` release writeback cookie pins.
- `netfs_invalidate_folio()` updates zero-point tracking and trims/removes netfs private folio metadata.
- `netfs_release_folio()` refuses dirty/busy folios, waits for deprecated private_2 when safe, and notes cache page release.
- Collector wait helpers support either workqueue-offloaded collection or in-caller collection.
- Pause wait helpers are used during retry coordination.

Concurrency notes:
- Uses request waitqueue and `NETFS_RREQ_IN_PROGRESS`, `NETFS_RREQ_PAUSE`, and subrequest in-progress flags.
- Wakes collection only when front subrequests complete or retrying requires reassessment.

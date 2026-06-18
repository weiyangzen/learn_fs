# File Research: sources/os/linux/linux-stable/fs/nfs/read.c

Purpose: Implements NFS buffered read and readahead using folios, pageio aggregation, netfs integration, and async RPC completion.

Key responsibilities:
- Allocates/frees read pageio headers from `nfs_read_data` slab cache.
- Initializes read pageio descriptors, choosing pNFS layout-driver read ops when available unless forced to MDS.
- Handles read completion:
  - marks folios uptodate once all grouped requests are complete,
  - zero-fills EOF or partial-read gaps,
  - records per-open-context errors,
  - completes netfs read accounting.
- Handles short reads by retrying the remaining byte range or forcing MDS retry for non-RPC pNFS drivers.
- Implements `nfs_read_folio` and `nfs_readahead`:
  - flushes pending writes before a locked folio read,
  - rejects stale inodes,
  - tries `nfs_netfs_*` first,
  - falls back to direct NFS pageio.

Integration:
- Uses version-specific `NFS_PROTO(inode)->read_setup/read_done`.
- Feeds common pageio via `nfs_pageio_init`, `nfs_pageio_add_request`, and `nfs_pageio_complete`.
- Integrates with fscache/netfs, pNFS, delegation atime updates, tracepoints, and NFS I/O stats.

Risks and notes:
- Read path assumes no mirrored reads and warns if mirror count differs from one.
- EOF handling depends on `good_bytes` and request ordering.
- File-less readahead must discover a readable open context or fails with `-EBADF`.

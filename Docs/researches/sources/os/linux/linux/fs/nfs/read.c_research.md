# File Research: sources/os/linux/linux/fs/nfs/read.c

Implements buffered read and readahead page I/O for the NFS client.

Key behavior:
- Allocates and frees read `nfs_pgio_header` objects through the `nfs_read_data` slab cache.
- `nfs_pageio_init_read()` selects ordinary MDS read I/O or pNFS layout-driver read ops, then initializes the generic NFS pageio descriptor.
- Read completion walks completed `nfs_page` requests, handles EOF zero-fill, marks successful folio ranges uptodate, records errors in the open context, unlocks folios, and notifies netfs completion.
- Handles short reads by retrying from the returned byte count, or forcing MDS retry for non-RPC layout drivers.
- `nfs_read_add_folio()` creates a read request for the valid portion of a folio, zero-fills beyond EOF within the folio, and queues it in pageio.
- `nfs_read_folio()` flushes conflicting pending writes, handles stale inodes, tries the netfs read path first, then falls back to NFS pageio.
- `nfs_readahead()` similarly tries netfs readahead first, then builds NFS pageio requests from the readahead control.
- Maintains read statistics and delegated atime updates.

Important interactions:
- Depends on protocol-specific `NFS_PROTO(inode)->read_done()` and `read_setup()` callbacks.
- Integrates with pNFS through layout-driver read ops and MDS reset support.
- Integrates with FS-Cache/netfs via `nfs_netfs_read_folio()`, `nfs_netfs_readahead()`, and related completion hooks.

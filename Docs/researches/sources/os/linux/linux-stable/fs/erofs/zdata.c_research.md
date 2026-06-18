# File Research: sources/os/linux/linux-stable/fs/erofs/zdata.c

This file implements compressed EROFS data readout: pcluster lifecycle, compressed-page caching, bio submission, decompression queues, read_folio, and readahead.

Major responsibilities:
- Defines `struct z_erofs_pcluster`, which tracks one compressed physical cluster, its compressed pages, output bvecs, decompression length, algorithm, offsets, cache state, and queue linkage.
- Creates pcluster slab caches sized for different maximum compressed cluster page counts.
- Optionally creates per-CPU kthread workers and CPU hotplug hooks for decompression work.
- Initializes global compression state in `z_erofs_init_subsystem()` and tears it down in `z_erofs_exit_subsystem()`.
- Creates a per-superblock managed-cache inode and xarray in `z_erofs_init_super()`.
- Registers or reuses pclusters in `managed_pslots`, using lockref, xarray compare/exchange, RCU freeing, and shrinker-visible refcount state.
- Binds compressed data to the managed cache when cache strategy and mapping conditions prefer cached I/O.
- Builds output bvec chains for file folios and chooses whether pages can be used for inplace I/O.
- Submits compressed-data bios to block devices, file-backed I/O, or fscache, then kicks decompression after bio completion.
- Decompresses pclusters into primary output pages and secondary copies, handling overlap, short-lived bounce pages, cached folios, inline metadata data, and partial decompression.
- Implements `z_erofs_read_folio()` and `z_erofs_readahead()` address-space operations.

Key concurrency/lifetime details:
- Pcluster fields are divided by comments into initialization-only, pcluster-lock protected, and atomic/parallel fields.
- `pcl->lock` serializes pcluster decompression and bvec state reset.
- `pcl->lockref` protects reuse/release and coordinates xarray shrinker removal.
- Existing pclusters can be linked into a request chain or recognized as inflight, avoiding duplicate decompression.
- Managed compressed folios use folio private data to remember their pcluster; release/invalidate hooks detach them only when safe.
- Pcluster freeing is RCU-delayed after xarray removal because lookup/release paths can race.

Read path:
- `z_erofs_scan_folio()` maps logical ranges with `z_erofs_map_blocks_iter()`, handles fragments, holes, inline/meta pclusters, and mapped compressed pclusters, and adds split online-folio accounting.
- `z_erofs_submit_queue()` separates bypass queues from queues requiring I/O, merges adjacent bio vectors, marks readahead I/O, and uses PSI memstall annotations for workingset pages.
- `z_erofs_runqueue()` chooses synchronous foreground decompression or background work based on `sync_decompress` and readahead size.
- Readahead scans folios in reverse order for better metadata I/O behavior and may expand around whole pclusters.

Important error behavior:
- Bio errors set queue `eio`, resulting in `-EIO` decompression completion.
- Decompressor string errors become `-EFSCORRUPTED`; error pointers propagate directly.
- Failed compressed page allocation records an error pointer in the compressed bvec and is surfaced during input parsing.
- All online folios are ended with success or error, and temporary pagepool pages are released after each request.

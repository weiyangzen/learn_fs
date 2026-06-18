# File Research: sources/os/linux/linux/fs/nfs/write.c

Implements buffered NFS writeback, dirty folio tracking, unstable-write COMMIT handling, writeback congestion, pNFS write integration, and write/commit cache initialization.

Key behavior:
- Allocates write and commit headers from slab caches backed by mempools for low-memory writeback safety.
- Tracks optional I/O-completion callbacks with a small refcounted `nfs_io_completion` object, used to trigger commits after writeback batches.
- Associates dirty folios with `nfs_page` request groups through `folio->private`, `PG_MAPPED`, and inode request counts.
- Merges subrequests into a single head request when writeback or update paths need a coherent per-folio request range.
- Grows local inode size for extending writes, updates delegated mtime when available, and invalidates FS-Cache state after local size changes.
- Records writeback errors in the address space and superblock errseq, then invalidates cached size/change/data state.
- Implements NFS writeback congestion using `nfs_congestion_kb`, per-server writeback counters, a congestion flag, and a waitqueue.
- `nfs_writepages()` batches dirty folios through pageio, optionally waits for congestion to clear, supports eager/write-wait policy, and queues follow-up commits for unstable writes.
- Commit-list helpers add/remove requests requiring COMMIT, including pNFS data-server commit-list integration.
- `nfs_write_completion()` removes completed write requests, records errors, marks unstable writes for commit with verifiers, or removes requests after stable writes.
- `nfs_try_to_update_request()` coalesces compatible dirty regions or flushes incompatible/non-contiguous requests before creating a new one.
- `nfs_flush_incompatible()` flushes existing folio requests owned by a different open context, lock owner, or dropped folio before buffered writes proceed.
- Credential expiry logic avoids unsafe buffered writes when RPC credential keys are expired or near timeout.
- `nfs_update_folio()` optionally expands writes to page-sized regions when cache state, locking, delegation, and mount flags make it safe.
- `nfs_initiate_write()` selects RPC priority, marks swapfile tasks, calls version-specific write setup, and traces submission.
- Write completion checks server stability promises, records unstable writes, handles short writes by retrying or escalating to stable writes, and invalidates mode on suid/sgid removal cases.
- Commit handling scans commit lists, submits pNFS or MDS COMMIT calls, verifies returned write verifiers, removes successfully committed requests, and redirties mismatches for rewrite.
- Provides synchronous inode, whole-file, and single-folio writeback helpers used by close, fsync, read-before-write, reclaim, and migration.
- `nfs_migrate_folio()` blocks migration while private NFS requests are attached unless synchronous migration can flush them first.
- Initializes and destroys write/commit slab caches and mempools, and computes the default congestion threshold from system memory capped at 256 MiB.

Important interactions:
- Uses generic NFS pageio and protocol-specific `write_setup`, `write_done`, `commit_setup`, and `commit_done`.
- Integrates with pNFS through layout-driver write ops, data-server commit lists, and MDS fallback.
- Integrates with FS-Cache/netfs, NFS delegations, file locking, writeback control, and VFS dirty/writeback accounting.

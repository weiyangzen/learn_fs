# File Research: sources/os/linux/linux-stable/fs/nfs/write.c

Purpose: Implements NFS buffered writeback, dirty folio request tracking, unstable-write commit handling, pNFS commit integration, write congestion, and writeback cache initialization.

Key responsibilities:
- Allocates write and commit headers through slab caches backed by mempools.
- Tracks folio-associated `nfs_page` requests through folio private data and inode request counts.
- Joins multiple subrequests for a folio before writeback, removing them from write/commit lists safely.
- Implements VFS writeback:
  - `nfs_writepages`,
  - `nfs_writepage_locked`,
  - `nfs_do_writepage`,
  - per-folio writeback/commit helpers.
- Updates or creates dirty write requests through `nfs_update_folio`.
- Flushes incompatible requests when a write comes from a different open context or lock owner.
- Implements optional whole-page write extension when safe, unless disabled by mount option or sync mode.
- Handles async write completion:
  - stable writes remove requests,
  - unstable writes move requests to commit lists,
  - errors mark mapping/superblock writeback errors and invalidate cached state.
- Implements COMMIT lifecycle:
  - scans commit lists,
  - builds `nfs_commit_data`,
  - uses pNFS commit first when available,
  - falls back to MDS commit,
  - validates write verifier,
  - redirties data on verifier mismatch.
- Handles short writes by retrying from progress point or switching to stable writes.
- Provides writeback flush APIs such as `nfs_wb_all`, `nfs_wb_folio`, `nfs_wb_folio_cancel`, and reclaim/migration support.
- Initializes write congestion threshold based on memory, capped at 256 MiB.

Integration:
- Uses version-specific protocol hooks `write_setup`, `write_done`, `commit_setup`, `commit_done`, and `commit_rpc_prepare`.
- Cooperates with pNFS, localio commits, fscache invalidation, delegation timestamp handling, SUNRPC priorities, file locking, errseq writeback error reporting, and NFS tracing/stats.
- Sysctl `nfs_congestion_kb` controls congestion thresholds.

Risks and notes:
- Request lifetime and page-group locking are complex; correctness depends on `PG_*` flags and krefs.
- Commit verifier mismatch triggers rewrite to protect against server restart/unstable data loss.
- Non-fatal write errors may redirty and retry, while fatal server errors launder requests and invalidate state.

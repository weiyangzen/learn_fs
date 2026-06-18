# File Research: sources/os/linux/linux-stable/fs/ceph/addr.c

## Purpose

`addr.c` implements CephFS address-space operations: buffered reads through netfs, buffered and mmap writes, writeback to OSDs, inline-data handling, FS-Cache write-through hooks, and per-pool read/write permission probing. It is the bridge between Linux page-cache/netfs folios and Ceph OSD object I/O.

## Main Responsibilities

- Defines `ceph_aops`, including `netfs_read_folio`, `netfs_readahead`, `ceph_writepages_start`, `ceph_write_begin`, `ceph_write_end`, `ceph_dirty_folio`, and invalidate/release/migrate handlers.
- Tracks dirty folios by attaching a `ceph_snap_context` to folio private data.
- Preserves Ceph snapshot ordering: writeback must flush dirty folios in ascending snap context order before newer head data.
- Issues OSD reads and writes, including sparse reads for encrypted files or `SPARSEREAD`.
- Integrates with `netfs_request_ops` via `ceph_netfs_ops`.
- Handles inline data reads and uninlining file data into OSD objects.
- Provides Ceph-specific mmap fault and page-mkwrite behavior.
- Caches and validates pool read/write permissions using OSD stat/create probes.

## Key Data Flow

Reads:
- `ceph_init_request()` prepares readahead state and acquires cache/read caps when needed.
- `ceph_netfs_prepare_read()` limits each subrequest to object and mount `rsize` boundaries.
- `ceph_netfs_issue_read()` chooses inline data, normal OSD read, or sparse OSD read.
- `finish_netfs_read()` updates metrics, handles `-ENOENT` as zero-fill, decrypts sparse encrypted extents, releases OSD data pages, and terminates the netfs subrequest.

Writes:
- `ceph_write_begin()` delegates preparation to netfs and then waits for deprecated private-2 cache write state.
- `ceph_write_end()` updates inode size, marks the folio dirty, and triggers cap checks if size changed.
- `ceph_dirty_folio()` increments global and inode dirty counters and attaches the current head or pending capsnap snap context.
- `ceph_writepages_start()` selects the oldest writable snap context, batches dirty folios, builds OSD write requests, and submits async writeback.
- `writepages_finish()` cleans folios, detaches snap contexts, updates dirty accounting, handles errors/blocklisting, and releases writeback refs.

## Snapshot and Dirty Accounting

The file’s central invariant is that dirty data is associated with exactly one snap context:
- Head writes increment `ci->i_wrbuffer_ref_head`.
- Writes racing snapshot creation can be charged to the newest pending `ceph_cap_snap`.
- `get_oldest_context()` finds the only snap context eligible for writeback.
- `ceph_find_incompatible()` prevents dirtying a folio under a newer context while it still contains dirty data for an older context.
- `ceph_put_wrbuffer_cap_refs()` in `caps.c` is called after writeback or invalidation to decrement per-head or per-capsnap counters.

This is why full-folio invalidation detaches private snap context and adjusts wrbuffer refs, while partial invalidation refuses to modify dirty accounting.

## Writeback Mechanics

Writeback uses `struct ceph_writeback_ctl` to carry selected snap context, file size/truncation metadata, range scan state, batching state, page arrays, and OSD op layout.

Important behavior:
- `ceph_define_writeback_range()` ignores caller writeback ranges for non-head snap contexts because older snapshot data must flush first.
- `ceph_process_folio_batch()` filters folios by mapping, dirty state, snap context, EOF, strip-unit boundaries, and writeback/private-2 state.
- `ceph_submit_write()` converts batches into one or more OSD write ops, splitting discontiguous page ranges into multiple extents.
- Encrypted writes use fscrypt bounce pages and round lengths to `CEPH_FSCRYPT_BLOCK_SIZE`.
- Writeback congestion is tracked with `fsc->writeback_count` and mount `congestion_kb` thresholds.

## Inline Data

Inline data is handled separately from normal object data:
- Reads can fetch inline data via an MDS `GETATTR` request in `ceph_netfs_issue_op_inline()`.
- `ceph_fill_inline_data()` installs inline bytes into page cache.
- `ceph_uninline_data()` creates object data, writes page-cache content into OSD object 0, guards with the `inline_version` xattr, and marks caps dirty after switching to `CEPH_INLINE_NONE`.

## mmap Behavior

- `ceph_filemap_fault()` acquires cache/lazy caps before calling `filemap_fault()`, or manually loads inline data for inline files.
- `ceph_page_mkwrite()` acquires buffer/write caps, updates times and i_version, resolves incompatible snap contexts, marks the folio dirty, and marks write caps dirty.

Signals are blocked except `SIGKILL` during cap acquisition around faults.

## FS-Cache Integration

When `CONFIG_CEPH_FSCACHE` is enabled:
- Dirty folios call `ceph_fscache_dirty_folio()`.
- Writeback marks pages with private-2 and calls `fscache_write_to_cache()`.
- Failed cache writes invalidate the cache except `-ENOBUFS`.

Without FS-Cache, these helpers compile to no-ops or normal `filemap_dirty_folio`.

## Pool Permission Checks

`ceph_pool_perm_check()` lazily validates read/write permission for regular file data pools:
- Skips snapshots and `NOPOOLPERM`.
- Uses an rb-tree cache keyed by pool id and namespace.
- Probes read with OSD `STAT` and write with exclusive `CREATE`.
- Caches `POOL_READ` and `POOL_WRITE` bits into inode flags if layout is unchanged.

## Important Dependencies

- `caps.c`: cap acquisition/release, dirty cap marking, wrbuffer ref release, writeback queueing.
- `cache.c`/`cache.h`: FS-Cache cookie helpers.
- `crypto.c`/`crypto.h`: encrypted read/write alignment, bounce pages, extent decryption.
- OSD client APIs: `ceph_osdc_new_request()`, `ceph_osdc_start_request()`, OSD op data setup.
- netfs library: request ops, folio read/readahead/write-begin support.

## Edge Cases and Risks

- Dirty folio accounting depends on every private snap context being detached exactly once.
- Non-head snapshot writeback intentionally ignores requested ranges; callers expecting strict range-limited writeback must account for Ceph snapshot ordering.
- Encrypted reads currently use page arrays rather than iter data because decryption infrastructure is page-based here.
- `ceph_netfs_issue_read()` mutates `subreq->io_iter.count` for encrypted reads to satisfy sparse message constraints.
- Forced unmount/shutdown converts operations to `-EIO`/`-ESTALE` and may invalidate or redirty pages.

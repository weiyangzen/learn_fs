# File Research: sources/os/linux/linux/fs/ceph/addr.c

## Purpose
Implements CephFS address-space, page-cache, netfs, writeback, mmap fault, inline-data, and OSD pool-permission behavior for regular file data. This is the core bridge between Linux VFS/mm folios, Ceph MDS capabilities/snapshots, and Ceph OSD object I/O.

## Main Responsibilities
- Provides `ceph_aops`, the Ceph address-space operations:
  - `read_folio = netfs_read_folio`
  - `readahead = netfs_readahead`
  - `writepages = ceph_writepages_start`
  - `write_begin = ceph_write_begin`
  - `write_end = ceph_write_end`
  - `dirty_folio = ceph_dirty_folio`
  - `invalidate_folio = ceph_invalidate_folio`
- Provides `ceph_netfs_ops` for netfs read integration and write-begin validation.
- Tracks dirty folio snap contexts through folio private data.
- Enforces Ceph snapshot writeback ordering.
- Submits asynchronous batched OSD writes and synchronous single-folio writes.
- Handles encrypted file block alignment, sparse reads, and fscrypt bounce pages.
- Handles inline data fetch and conversion to normal object-backed file data.
- Handles mmap faults and `page_mkwrite`.
- Caches OSD pool read/write permission probes.

## Key Data and Invariants
- Dirty folios store a `struct ceph_snap_context *` in `folio->private`.
- Dirty page accounting is split between:
  - `ci->i_wrbuffer_ref`
  - `ci->i_wrbuffer_ref_head`
  - per-`ceph_cap_snap->dirty_pages`
  - global `mdsc->dirty_folios`
- Writeback must submit dirty folios in snapshot order. `get_oldest_context()` determines the oldest writable snap context.
- A folio dirty in a newer snap context cannot be modified until the older context is written or known written.
- Encrypted reads/writes are rounded to `CEPH_FSCRYPT_BLOCK_SIZE`; page offsets are normalized through `ceph_fscrypt_page_offset()` and `ceph_fscrypt_pagecache_page()`.

## Read Path
- `ceph_netfs_expand_readahead()` adjusts netfs readahead to Ceph stripe-unit boundaries while respecting file readahead settings and `FMODE_RANDOM`.
- `ceph_init_request()` sets request flags, allocates Ceph netfs private state, and may acquire read/cache caps for readahead callers that do not already hold them.
- `ceph_netfs_prepare_read()` limits subrequest length to the current object mapping and mount `rsize`.
- `ceph_netfs_issue_read()`:
  - rejects shutdown inodes with `-EIO`;
  - uses MDS inline-data fetch when `ceph_has_inline_data(ci)`;
  - adjusts encrypted I/O to crypto block boundaries;
  - allocates OSD read or sparse-read requests;
  - uses page arrays for encrypted reads and iter data for unencrypted reads;
  - pins OSD stopping blockers until completion.
- `finish_netfs_read()`:
  - records metrics;
  - maps `-ENOENT` to a successful hole/tail clear;
  - marks blocklisted clients on `-EBLOCKLISTED`;
  - decodes sparse extents;
  - decrypts encrypted extents through `ceph_fscrypt_decrypt_extents()`;
  - sets netfs transferred/error fields and terminates the subrequest.

## Dirtying and Invalidation
- `ceph_dirty_folio()`:
  - refuses already dirty folios;
  - chooses pending cap-snap context or head snap context;
  - increments Ceph dirty/writebuffer counters;
  - holds an inode reference on transition from zero dirty buffers;
  - attaches snap context to the folio;
  - delegates final dirty marking to fscache/netfs.
- `ceph_invalidate_folio()` only adjusts Ceph dirty accounting for full-folio invalidation. Partial invalidation leaves dirty accounting intact.
- Full invalidation detaches the snap context and calls `ceph_put_wrbuffer_cap_refs()`.

## Writeback Path
- `ceph_writepages_start()` drives asynchronous writeback:
  - skips nonblocking writeback under congestion;
  - rejects forced unmount/shutdown;
  - initializes `ceph_writeback_ctl`;
  - pins OSD stopping blocker;
  - repeatedly selects oldest snap context and walks tagged folios;
  - tags pages for integrity writeback when required;
  - batches contiguous or multi-extent writes up to stripe/object and OSD op limits.
- `ceph_process_folio_batch()` filters candidate folios:
  - waits on existing writeback and fscache private state;
  - locks folios;
  - rejects wrong snap context, beyond-EOF folios, and strip-unit overrun;
  - clears dirty state for I/O;
  - allocates page arrays;
  - encrypts folios into bounce pages for encrypted files.
- `ceph_submit_write()` builds and starts OSD write requests:
  - may split into several OSD requests when op count is too large;
  - attaches pages to each extent op;
  - starts fscache write-through for each extent;
  - sets writeback state;
  - transfers page-array ownership to the OSD request.
- `writepages_finish()`:
  - maps OSD errors to mapping errors and Ceph write-error state;
  - releases bounce pages;
  - detaches snap contexts;
  - ends page writeback;
  - decrements dirty-folio and writeback congestion counters;
  - optionally removes pages when cache/lazy caps were lost;
  - releases writebuffer cap refs and OSD blocker.
- `write_folio_nounlock()` is the synchronous single-folio fallback used when a folio dirty in an older snap context must be written before modification.

## Write-Begin and Write-End
- `ceph_find_incompatible()` detects folios dirty under a conflicting snap context.
- `ceph_netfs_check_write_begin()` unlocks/drops incompatible folios, queues writeback, waits for the conflicting context to become writable or written, and returns `-EAGAIN`.
- `ceph_write_begin()` delegates to `netfs_write_begin()` and waits for fscache private state.
- `ceph_write_end()` marks uptodate, updates i_size, marks dirty, and calls `ceph_check_caps()` when size growth needs cap reporting.

## mmap Integration
- `ceph_filemap_fault()` obtains read/cache/lazy caps before `filemap_fault()`. If inline data is present and cache caps are unavailable, it fetches inline data into page 0.
- `ceph_page_mkwrite()` obtains write/buffer/lazy caps, updates file time and i_version, handles snapshot-context conflicts, marks the folio dirty, and marks `CEPH_CAP_FILE_WR` dirty metadata.

## Inline Data
- `ceph_fill_inline_data()` fills page-cache page 0 from MDS-provided inline bytes.
- `ceph_uninline_data()` converts inline file data to OSD object data:
  - obtains the current inline version;
  - gets a snap context;
  - reads page 0;
  - creates the first object;
  - writes page contents with xattr compare/set operations on `inline_version`;
  - marks inline metadata dirty as `CEPH_INLINE_NONE`.

## Pool Permission Cache
- `__ceph_pool_perm_get()` probes a data pool/namespace by issuing OSD `STAT` and `CREATE` requests against the first object name, then stores read/write permission bits in an rb-tree.
- `ceph_pool_perm_check()` skips non-regular files, snapshots, and `NOPOOLPERM`; otherwise caches permission flags in inode state and returns `-EPERM` when requested caps exceed pool rights.
- `ceph_pool_perm_destroy()` frees the MDS client permission tree.

## External Dependencies
- Linux mm/filemap/netfs/fscache APIs.
- Ceph MDS caps from `caps.c`.
- Ceph OSD client request construction and striper mapping.
- Ceph fscrypt helpers from `crypto.c`/`crypto.h`.
- Ceph metrics and subvolume metrics.

## Risk Notes
- Dirty folio private data and cap dirty counters must stay synchronized; missed detach/ref puts can leak snap contexts or inode refs.
- Snapshot writeback ordering is critical for correctness.
- Encrypted I/O relies on block-aligned OSD requests and correct bounce-page ownership.
- Forced unmount/shutdown paths deliberately convert pending dirty state to mapping errors.
- Pool permission probing writes/creates first-object metadata for head inodes, so snapshots are explicitly skipped.

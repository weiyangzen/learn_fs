# File Research: sources/os/darwin/xnu/bsd/vfs/vfs_cluster.c

## Scope And Role

`vfs_cluster.c` implements Darwin/XNU clustered vnode I/O over UBC/UPL pages. It is the main VFS helper layer for page-in, page-out, cached reads/writes, direct I/O, physically contiguous I/O, read-ahead, write-behind, sparse dirty-page tracking, buffer transaction completion, verification, throttling, and UPL copy helpers.

The file bridges vnode/VNOP filesystem block mapping with VM-backed file pages and user/kernel `uio` buffers. It decides whether an operation should use the cache-copy path, direct UPL path, or contiguous physical-memory path, splits work into device-sized buffer transactions, tracks completion, and commits or aborts UPL ranges with the correct page-cache semantics.

## Main State And Constants

Important flags and tuning knobs include:

- `CL_READ`, `CL_WRITE`, `CL_ASYNC`, `CL_COMMIT`, `CL_PAGEIN`, `CL_PAGEOUT`, `CL_DIRECT_IO`, `CL_DEV_MEMORY`, `CL_PRESERVE`, `CL_THROTTLE`, `CL_NOCACHE`, `CL_ENCRYPTED`, and related internal cluster I/O flags.
- `MAX_IO_REQUEST_SIZE`, `MAX_IO_CONTIG_SIZE`, `MAX_VECTOR_UPL_SIZE`, `MIN_DIRECT_WRITE_SIZE`, and `MAX_VECTS` bound request and vector UPL sizes.
- `speculative_prefetch_max`, `speculative_prefetch_max_iosize`, `prefetch_max`, `overlapping_read_max`, `overlapping_write_max`, and throttle sizing sysctls tune read-ahead and concurrency.
- `split_pgin`, `split_all_pgin`, `split_all_pgin_equal`, and `split_pgin_headio` control SSD split-pagein behavior.

Important data structures:

- `struct clios`: per-stream completion state for asynchronous clustered I/O, with issued/completed byte counts, first error, wanted flag, and mutex.
- `struct cl_readahead`: UBC-owned read-ahead state, lock, last read page, current read-ahead length, and maximum read-ahead page.
- `struct cl_writebehind`: UBC-owned write-behind state, lock, normal cluster array, sparse cluster map, sequential write accounting, and fsync/sparse-push serialization counters.
- `struct cl_direct_read_lock`: hashed per-vnode read/write lock used to serialize direct-read cache absence checks against clients that need stable cache state.
- `struct verify_buf`: queue entry for asynchronous verification worker threads.
- `struct vfs_drt_clustermap` and `struct vfs_drt_hashentry`: dirty-region tracking map for sparse dirty page clusters.

## Initialization And Sizing

`cluster_init()` initializes the direct-read lock hash lists and the verification queues. `cluster_max_io_size()` derives the effective maximum I/O size from mount read/write segment counts and max counts, clamps to UPL limits, and enforces at least the old fixed `MAX_UPL_TRANSFER_BYTES` floor.

`cluster_max_prefetch()`, `calculate_max_throttle_size()`, and `calculate_max_throttle_cnt()` scale prefetch and throttling by mount I/O scale and SSD status from `vfs_disk_conditioner`.

Per-vnode read-ahead and write-behind contexts are lazily allocated through `cluster_get_rap()` and `cluster_get_wbp()`, stored in `vp->v_ubcinfo`, and protected by vnode locks during first assignment.

## Core Transaction Engine

`cluster_io()` is the central engine. It accepts a vnode, UPL, UPL offset, file offset, size, cluster flags, optional real buffer, optional `clios` stream state, and optional completion callback. It:

1. Rounds sizes for cached page-backed I/O while avoiding unwanted rounding for direct/device-memory paths.
2. Selects read or write buffer flags and VNOP blockmap flags.
3. Queries `VNOP_VERIFY` for page-size verification support on eligible reads and pageins.
4. Applies throttling limits, pagein/pageout, cache, passive, encrypted, raw-encrypted, direct, and metadata flags.
5. Handles direct-write associated UPL creation to lock and later dump stale cached pages that overlap uncached writes.
6. Iterates over extents from `VNOP_BLOCKMAP`, clipping to device/mount limits and max vector count.
7. Handles file holes:
   - read holes are zero-filled into the UPL and committed as valid pages;
   - write holes on pageout can fall back to `vnode_pageout()` for individual pages.
8. Builds chained `buf_t` transactions, assigns `b_trans_head`/`b_trans_next`, UPL offsets, logical and physical block numbers, callback state, and verification flags.
9. Issues buffers through `VNOP_STRATEGY()`.
10. Marks transaction end with `cluster_EOT()` and completes synchronous transactions via `cluster_complete_transaction()`.

The transaction machinery uses `cluster_iodone()`, `cluster_iodone_finish()`, `cluster_wait_IO()`, and `cluster_complete_transaction()` to wait for all buffers in a transaction, aggregate residuals/errors, run callbacks, zero EOF tails, run verification, update stream completion state, commit or abort UPL ranges, free internal buffers, and complete any original caller buffer.

## Verification Path

The file supports filesystem read verification through `VNOP_VERIFY`.

`cluster_EOT()` may allocate a verification context for a transaction and starts verification worker threads lazily up to `num_verify_threads`. `cluster_iodone()` queues eligible transactions to `verify_work_head` when async verification is possible; otherwise completion verifies inline.

`cluster_handle_verification()` verifies precomputed hashes when present, otherwise maps the UPL range with `ubc_upl_map_range()`, calls `VNOP_VERIFY` with the context, then unmaps and frees the context. `verify_in_flight` and UPL map-exclusive state prevent concurrent mapping conflicts on the same UPL.

Errors from verification are folded into normal I/O completion. If a transaction declared `BA_WILL_VERIFY` but has no context, completion returns `EBADMSG`.

## Error And UPL Completion Semantics

`cluster_ioerror()` chooses UPL abort/commit behavior based on direct I/O, pagein/pageout, cache-preserve, write error type, and swap vnode status. Pageins may abort with `UPL_ABORT_ERROR`; transient write/pageout errors usually leave pages unchanged; non-cached read failures dump pages.

`cluster_handle_associated_upl()` handles the special associated UPL used by direct uncached writes to protect cached pages while disk writes are outstanding. It computes the associated UPL range even for unaligned UPL/file offsets, marks shared first/last pages across transactions, aborts/dumps completed associated ranges, and deallocates the associated UPL when empty.

## Pagein And Pageout Entry Points

`cluster_pageout()` and `cluster_pageout_ext()` validate readonly mounts, offsets, page alignment, EOF bounds, UPL commit flags, and encryption flags before issuing `cluster_io()` with `CL_PAGEOUT | CL_THROTTLE`, optionally async and commit.

`cluster_pagein()` and `cluster_pagein_ext()` validate UPL, offset, EOF, and page alignment. They abort invalid tails beyond EOF and issue `cluster_io()` with `CL_READ | CL_PAGEIN`.

`cluster_handle_split_pagein()` optionally splits large SSD pageins so the page that caused the fault is read first, with optional head I/O and equal 32 KiB chunks controlled by globals. This improves fault latency while still issuing remaining I/O.

`cluster_bp()` and `cluster_bp_ext()` adapt a traditional `buf_t` to clustered I/O using the vnode block-to-offset conversion.

## Read Path

`cluster_read()` and `cluster_read_ext()` choose among:

- `cluster_read_copy()` for cached UBC copy reads;
- `cluster_read_direct()` for aligned no-cache/user-space or encrypted direct reads;
- `cluster_read_contig()` for physically contiguous memory;
- `cluster_io_type()` to classify the current `uio` vector.

`cluster_read_copy()` first tries to satisfy data from UBC via `cluster_copy_ubc_data_internal()`. On misses, it creates a UPL, finds invalid page ranges, issues async `cluster_io()` for missing pages, waits for completion, copies valid data to the `uio`, and commits or aborts pages depending on error and no-cache status. It manages read-ahead state, speculative prefetch, throttling, BootCache-aware throttle exceptions, and cache-reference decisions based on I/O policy.

`cluster_read_direct()` handles aligned direct reads into user/kernel buffers. It checks device block alignment, mount memory alignment, verification-block alignment, encrypted read constraints, and sub-page user maps. It may copy cache-resident pages first unless raw encrypted data is requested. It uses hashed direct-read locks around cache absence checks, creates wired UPLs for the destination, supports vector UPLs for multi-iov requests, overlaps async I/O up to read-ahead limits, prefaults user pages afterward for pmap accounting, and falls back to `cluster_read_copy()` for unhandled tails unless encrypted I/O forbids fallback.

`cluster_read_contig()` handles physically contiguous targets by using UPL physical addresses and `cluster_align_phys_io()` for unaligned heads/tails. Aligned middle ranges are sent as `CL_DEV_MEMORY` async clustered reads.

## Write Path

`cluster_write()` and `cluster_write_ext()` choose among:

- `cluster_write_copy()` for cached copy writes and zero-fill operations;
- `cluster_write_direct()` for aligned no-cache user writes;
- `cluster_write_contig()` for physically contiguous memory;
- fallback from direct to cached when direct I/O is unsupported.

`cluster_write_ext()` handles vnode `VNOCACHE_DATA`, passive flags, no-cache/direct policy, `IO_NOCACHE_SWRITE` filesystem-block direct-write opt-in, head/tail zero-fill incompatibility with direct I/O, and large request chunking.

`cluster_write_direct()` creates wired UPLs over user buffers for aligned direct writes, optionally combines multiple vectors into vector UPLs, overlaps async writes using `clios`, throttles based on mount saturation and throttle windows, calls `cluster_syncup()` before the first direct write to flush delayed cached writes, and falls back to cached writes on `ENOTSUP`. It also supports filesystem block-size direct writes through `CL_DIRECT_IO_FSBLKSZ`.

`cluster_write_contig()` writes physically contiguous memory using UPL physical addresses. It handles unaligned device-block heads/tails with `cluster_align_phys_io()` and sends aligned middle ranges as `CL_DEV_MEMORY` async writes.

`cluster_write_copy()` handles cached writes and file growth zero-fill. It computes head/tail zero-fill ranges, optionally reads partial old pages before modifying them, copies user data into UPL pages with `cluster_copy_upl_data()`, zero-fills holes and EOF tails, commits pages dirty/inactive, and either pushes synchronously with `cluster_push_now()` or records delayed write clusters with `cluster_update_state_internal()`.

`cluster_zero_range()` avoids forced zeroing of already-valid pages when requested, preventing corruption of mmap-dirtied or already valid cache pages.

## Read-Ahead And Advisory Reads

`cluster_read_ahead()` tracks sequential access in `cl_readahead`, doubles read-ahead length up to mount-scaled limits, avoids prefetch when the target page is already present, and dispatches `cluster_read_prefetch()`.

`advisory_read()` and `advisory_read_ext()` issue passive speculative reads for ranges not already present in UBC. They create absent-only UPLs, find present page ranges returned by the UPL, and issue async `cluster_io()` with `CL_ASYNC | CL_READ | CL_COMMIT | CL_AGE`.

## Write-Behind And Push

`cluster_update_state()` and `cluster_update_state_internal()` record dirty write extents into the per-vnode write-behind context. The normal path keeps up to `MAX_CLUSTERS` clustered extents, merges adjacent/overlapping writes, tracks sequential writes, and pushes some clusters early when not deferring writes. When normal clustering cannot represent the pattern, it switches to sparse dirty-region tracking.

`cluster_push()`, `cluster_push_ext()`, and `cluster_push_err()` flush delayed clusters. They honor deferred-write mounts, serialize fsync-like pushes with sparse-push state, wait for active sparse pushes when synchronous, push sparse maps or normal clusters, and wait for vnode writes for `IO_SYNC`.

`cluster_try_push()` sorts normal clusters by address, optionally avoids pushing non-sequential full cluster sets so the vnode can switch to sparse mode, calls `cluster_push_now()` for each cluster, and merges unpushed clusters back or converts them to sparse state if capacity is exceeded.

`cluster_push_now()` creates dirty-only UPLs for a cluster, trims to EOF, skips clean/precious pages, and writes dirty runs through `cluster_io()` with commit/age/throttle flags. For VM-initiated pushes it delegates to `vnode_pageout()`.

`cluster_release()` frees read-ahead/write-behind contexts and any sparse map when the UBC info is released.

## Sparse Dirty-Region Tracking

The `vfs_drt_*` implementation provides a variable-size circular hash table of page-bitvectors for sparse dirty regions. It is used when dirty writes are too random or numerous for the fixed normal cluster array.

Key behavior:

- Each hash entry represents `DRT_BITVECTOR_PAGES` pages aligned by `DRT_ADDRESS_MASK`.
- Maps grow from small to large to xlarge allocations depending on occupancy and available physical memory.
- `vfs_drt_mark_pages()` marks dirty pages and returns how many were newly marked.
- `vfs_drt_get_cluster()` finds the next contiguous dirty bit run, clears it from the map, and returns byte offset/length.
- `vfs_drt_control()` frees the map or resets the clean cursor.
- `vfs_get_scmap_push_behavior_internal()` asks xlarge maps to push all at once.

`sparse_cluster_switch()` converts normal clusters to sparse dirty bits by consulting UBC page dirty state. `sparse_cluster_add()` marks new sparse ranges, pushing existing sparse clusters if the map fills. `sparse_cluster_push()` drains dirty clusters through `cluster_push_now()` and restores dirty bits if a push fails.

## Copy Helpers

`cluster_copy_upl_data()` temporarily converts `uio_segflg` to the physical variant and copies between `uio` data and UPL physical pages with `uiomove64()`. It updates logical deferred write accounting and panics if asked to move into restricted physical pages.

`cluster_copy_ubc_data()` and `cluster_copy_ubc_data_internal()` copy directly through the vnode memory object using `memory_object_control_uiomove()`, optionally marking pages dirty and taking page references.

`cluster_align_phys_io()` handles sub-device-block physical I/O heads/tails by reading or creating a cache page, copying physical-to-physical with `copypv()`, writing back if needed, advancing the `uio`, and aborting the temporary UPL appropriately.

`is_file_clean()` scans UBC pages for dirty state and returns `EINVAL` if any dirty page is found.

## Direct-Read Locking

`cluster_lock_direct_read()` and `cluster_unlock_direct_read()` maintain a small global hash of per-vnode `lck_rw_t` locks with reference counts. Direct read paths take shared locks between cache-absence checks and I/O issue; external clients can take exclusive locks to prevent direct reads from racing state that must remain stable.

## Security, Correctness, And Edge Cases

This file is sensitive to page-cache correctness. Notable safeguards include:

- Panics for impossible transaction state, oversized real buffers, invalid vector UPL paths, failed mandatory UPL creation, verification sizing violations, and DRT count corruption.
- Strict alignment checks for pagein/pageout, direct I/O, encrypted reads, verification, device block sizes, and mount memory alignment.
- Special handling for AFP-style `mnt_devblocksize == 1`.
- Avoidance of direct I/O for sub-page-size user address spaces.
- Direct uncached writes synchronize dirty partial first/last cached pages and reject wired cached pages by falling back to cached writes.
- Pageout write holes are handled with nested `vnode_pageout()` to avoid deadlocks.
- Read throttling can bypass delay if BootCache reports the block is already cached.
- Sparse push failures preserve dirty state when possible and behave specially during shutdown for local removable/non-removable mounts.

## Dependencies

The implementation depends on XNU VM/UBC/UPL APIs, vnode/VNOP interfaces (`VNOP_BLOCKMAP`, `VNOP_STRATEGY`, `VNOP_VERIFY`), buffer cache internals, mount I/O limits and flags, task I/O accounting, throttling APIs, BootCache hooks, kdebug/DTrace tracing, physical copy primitives, and disk-conditioner SSD detection.

## Research Notes

The complete 8400-line source file was read. The file is the core Darwin clustered file I/O implementation: most complexity comes from preserving UBC page correctness while overlapping asynchronous filesystem I/O, adapting to direct/contiguous/cached buffer types, handling sparse dirty write patterns, and integrating filesystem verification and throttling without losing page dirty/error state.

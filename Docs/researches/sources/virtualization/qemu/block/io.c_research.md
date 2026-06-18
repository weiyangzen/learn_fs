# File Research: sources/virtualization/qemu/block/io.c

## Role

`block/io.c` is QEMU's central block-layer I/O implementation. It sits between block users and individual `BlockDriver` implementations, enforcing request validation, alignment, serialization, drain/quiesce semantics, dirty tracking, copy-on-read, zero/discard behavior, flushing, block-status traversal, copy-range delegation, truncation, VM-state I/O, zoned operations, and registered-buffer propagation.

This file is not a protocol or format driver. It is the shared I/O policy layer that normalizes requests before they reach drivers such as raw, qcow2, iSCSI, file-posix, linux-aio, and io_uring.

## Major Responsibilities

- Maintains parent drain notifications through `bdrv_parent_drained_begin()`, `bdrv_parent_drained_end()`, and `bdrv_parent_drained_poll()`.
- Refreshes inherited and driver-specific `BlockLimits` with `bdrv_refresh_limits()`.
- Tracks copy-on-read enablement with an atomic reference count via `bdrv_enable_copy_on_read()` and `bdrv_disable_copy_on_read()`.
- Implements top-level and all-node drain operations through `bdrv_drained_begin()`, `bdrv_drained_end()`, `bdrv_drain()`, `bdrv_drain_all_begin()`, `bdrv_drain_all_end()`, and related helpers.
- Tracks active requests in `BdrvTrackedRequest` lists so overlapping serializing requests wait instead of racing.
- Validates offsets, byte counts, I/O vectors, and maximum request sizes through `bdrv_check_qiov_request()`, `bdrv_check_request()`, and internal 32-bit bounded checks.
- Routes aligned reads, writes, compressed writes, write-zeroes, flushes, discards, ioctls, zoned operations, VM-state I/O, copy-range, and truncation requests to block drivers.
- Handles unaligned read/write padding with bounce buffers and read-modify-write cycles.
- Walks backing/filter chains for block allocation status and zero detection.

## Drain and Quiesce Model

The drain path prevents new activity and waits for in-flight operations to complete. `bdrv_do_drained_begin()` increments `bs->quiesce_counter`; on the first transition it notifies parents and calls `drv->bdrv_drain_begin` if present. If polling is requested, it waits while parent callbacks or `bs->in_flight` indicate work remains.

Coroutine callers cannot directly run the drain body, so `bdrv_co_yield_to_drain()` schedules a bottom half and yields. This prevents recursive coroutine entry and ensures drain operations run from an appropriate main-loop/global-state context. `bdrv_drain_all_begin()` applies this across all BDS nodes, while `bdrv_drain_all_begin_nopoll()` only quiesces and leaves polling to the caller.

Record/replay mode short-circuits all-node drains because waiting on the block queue can be non-terminating under replay semantics.

## Request Tracking and Serialization

`tracked_request_begin()` inserts a request into `bs->tracked_requests`; `tracked_request_end()` removes it and wakes any waiters. Requests can become serializing via `tracked_request_set_serialising()` or `bdrv_make_request_serialising()`, which expands the overlap range to an alignment boundary such as the cluster size.

`bdrv_find_conflicting_request()` detects overlapping serializing requests and makes the current coroutine wait on the conflicting request's queue. It asserts against reentrant self-waits, because a block driver issuing nested overlapping requests would deadlock. This is especially important for:
- copy-on-read cluster allocation,
- unaligned write read-modify-write,
- truncate preallocation/growth regions,
- explicit `BDRV_REQ_SERIALISING` write requests.

## Alignment, Padding, and Bounce Buffers

The block layer enforces `bs->bl.request_alignment`. Misaligned requests are padded by `bdrv_pad_request()` using `BdrvRequestPadding`.

For writes, padding requires read-modify-write: `bdrv_padding_rmw_read()` reads head/tail regions, then the write path merges caller data with preserved bytes. For reads, padding expands the request and copies back into the original iovec in `bdrv_padding_finalize()` if vector elements had to be collapsed.

`bdrv_create_padded_qiov()` ensures the padded vector never exceeds `IOV_MAX`; if needed it collapses initial vector elements into a temporary aligned bounce buffer. This avoids invalid vector submission while preserving the caller-visible layout.

## Read Path

`bdrv_co_preadv_part()` is the public coroutine read entry point. It:
- checks medium presence,
- validates request and qiov bounds,
- applies copy-on-read if `bs->copy_on_read` is nonzero,
- pads the request if required,
- tracks the request,
- calls `bdrv_aligned_preadv()`.

`bdrv_aligned_preadv()` handles copy-on-read serialization and dispatch. It fragments large reads by `bs->bl.max_transfer`, reads beyond EOF as zeroes, and strips copy-on-read once handled.

`bdrv_co_do_copy_on_readv()` implements copy-on-read. It rounds the affected area to subcluster or cluster boundaries, checks allocation, reads unallocated data through a bounce buffer, writes it back to the image using normal write or write-zeroes, then copies the requested bytes to the caller unless the request is a prefetch.

## Write and Zero-Write Path

`bdrv_co_pwritev_part()` validates and pads writes, tracks the request, and dispatches either normal writes or `BDRV_REQ_ZERO_WRITE`.

`bdrv_aligned_pwritev()` prepares the write with `bdrv_co_write_req_prepare()`, checks read-only/bitmap permissions, serializes if needed, updates write thresholds, detects all-zero buffers when `detect_zeroes` is enabled, and then dispatches one of:
- `bdrv_co_do_pwrite_zeroes()` for zero writes,
- `bdrv_driver_pwritev_compressed()` for compressed writes,
- `bdrv_driver_pwritev()` for regular writes.

Large writes are split by `max_transfer`; emulated FUA is applied only on the final chunk when the driver cannot support FUA natively.

`bdrv_co_do_pwrite_zeroes()` first tries the driver's efficient `bdrv_co_pwrite_zeroes` operation, honoring `BDRV_REQ_MAY_UNMAP`, `BDRV_REQ_NO_FALLBACK`, and FUA semantics. If unsupported and fallback is allowed, it writes an aligned zero-filled bounce buffer. It invalidates block-status cache ranges that overlap the zero write.

`bdrv_co_do_zero_pwritev()` handles unaligned zero writes by doing padding-specific read-modify-write for edge regions and efficient aligned zero writes for the middle.

## Driver Dispatch

Driver-facing helpers normalize old and new block driver APIs:
- `bdrv_driver_preadv()` supports `bdrv_co_preadv_part`, `bdrv_co_preadv`, `bdrv_aio_preadv`, or legacy sector-based `bdrv_co_readv`.
- `bdrv_driver_pwritev()` supports `bdrv_co_pwritev_part`, `bdrv_co_pwritev`, `bdrv_aio_pwritev`, or legacy sector-based `bdrv_co_writev`.
- `bdrv_driver_pwritev_compressed()` supports compressed write APIs.
- `CoroutineIOCompletion` bridges callback-style AIO into coroutine waits.

This file therefore preserves compatibility between coroutine-native drivers and older callback/sector-oriented drivers.

## Flush, Discard, and Cache Effects

`bdrv_co_flush()` coalesces concurrent flushes with `bs->active_flush_req`, uses `write_gen`/`flushed_gen` to skip redundant disk flushes, honors `BDRV_O_NO_FLUSH`, and recursively flushes writable children. It supports driver-level all-in-one flush, flush-to-OS, flush-to-disk, and legacy AIO flush.

`bdrv_flush_all()` flushes every BDS, including unreachable nodes, except under replay mode.

`bdrv_co_pdiscard()` validates discard support, respects `BDRV_O_UNMAP`, invalidates block-status cache, fragments requests based on `pdiscard_alignment` and `max_pdiscard`, tolerates rejected unaligned head/tail discards, and updates dirty/request tracking through the write-finish path.

## Block Status and Zero Detection

`bdrv_co_do_block_status()` is the core status query. It:
- clamps to image length,
- falls back to allocated data for drivers without block-status support,
- rounds queries to request alignment,
- uses block-status cache for protocol nodes with no children,
- handles filter nodes through `BDRV_BLOCK_RAW`,
- synthesizes allocation/zero status from backing chains,
- optionally recurses into underlying files to refine zero status.

`bdrv_co_common_block_status_above()` walks filter/COW chains above a base node. Public helpers include:
- `bdrv_co_block_status_above()`,
- `bdrv_co_block_status()`,
- `bdrv_co_is_zero_fast()`,
- `bdrv_co_is_all_zeroes()`,
- `bdrv_co_is_allocated()`,
- `bdrv_co_is_allocated_above()`.

`bdrv_co_is_all_zeroes()` has a fast block-status probe and a small allocated-head fallback read capped by `MAX_ZERO_CHECK_BUFFER`.

## Copy Range and Registered Buffers

`bdrv_register_buf()` and `bdrv_unregister_buf()` recursively propagate host buffer registration to drivers and children. Registration rollback unwinds already-registered children if a later registration fails.

`bdrv_co_copy_range_internal()` implements both source-recursive and destination-recursive copy-range delegation. It validates source and destination, rejects encrypted nodes and missing driver callbacks, tracks either a read or write request, and delegates to `bdrv_co_copy_range_from` or `bdrv_co_copy_range_to`.

## Truncate and Resize

`bdrv_co_truncate()` validates permissions and size, serializes newly grown regions, handles backing-file exposure by forcing zero-fill when growth would reveal backing data, calls driver/filter truncate, refreshes total sectors, updates dirty bitmaps, and notifies parents through resize callbacks.

## Other Interfaces

The file also provides:
- VM-state read/write helpers and buffer wrappers,
- synchronous AIO cancellation wrappers,
- `bdrv_co_ioctl()`,
- zoned block operations: report, management, append,
- aligned memory allocation helpers,
- in-flight cancellation dispatch,
- snapshot-specific read/status/discard helpers.

## Important Invariants

- Requests must not exceed `BDRV_MAX_LENGTH`; many driver-facing requests are further capped by `BDRV_REQUEST_MAX_BYTES`.
- Alignment-sensitive drivers receive aligned requests after padding or fragmentation.
- `bs->in_flight` is incremented around operations that must be visible to drain.
- Request serialization prevents overlapping cluster allocation, RMW, truncate, and explicit serializing writes from racing.
- Dirty bitmap and parent resize notifications are updated only after write/truncate success paths that change visible state.

# File Research: sources/virtualization/spdk/lib/bdev/bdev.c

This report was synthesized from ordered chunk research outputs.

## Chunk Map

- chunk 1: lines 1-9156, source bytes 262132, report `Docs/researches/chunks/chunk_sources_virtualization_spdk_lib_bdev_bdev_c_1_1_9156_78bb6577d9b7_research.md`
- chunk 2: lines 9157-11549, source bytes 63657, report `Docs/researches/chunks/chunk_sources_virtualization_spdk_lib_bdev_bdev_c_2_9157_11549_d81a8c267140_research.md`

## Chunk Research

### Chunk 1: lines 1-9156

# Chunk Research: sources/virtualization/spdk/lib/bdev/bdev.c lines 1-9156

## Scope

This chunk covers the first 9,156 lines of SPDK's generic block-device core. It includes global bdev manager setup, bdev option/config handling, module initialization/finalization, examine orchestration, per-thread/channel resources, public I/O submission APIs, split I/O, QoS, reset/abort paths, completion/status translation, registration/unregistration, and descriptor open setup. The chunk ends inside the async-open implementation; descriptor close, media events, claims v1/v2, LBA lock/unlock continuation, module registration, memory-domain queries, and trace registration continue in chunk 2.

## Core State

- `g_bdev_mgr` is the process-global registry: bdev I/O mempool, zero buffer, module list, bdev list, RB tree of names/aliases, subsystem init flags, spinlock, and pending async opens.
- `g_bdev_opts` controls bdev I/O pool/cache sizing, auto examine, and per-channel iobuf cache sizes. `spdk_bdev_get_opts()`/`spdk_bdev_set_opts()` use versioned struct-size field copying and validate mempool size against thread count.
- `spdk_bdev_channel` is the per-thread/per-bdev state: backend channel, accel channel, shared resource, outstanding counters, submitted/locked/accel/memory-domain queues, QoS queue, histogram, trace id, and replicated locked ranges.
- `spdk_bdev_shared_resource` is per management-channel plus backend `shared_ch`; it centralizes NOMEM retry queues, shared outstanding counters, a retry poller, and refcounting across bdev channels sharing the same backend channel.
- `spdk_bdev_desc` is an open handle with write permission, open options, owner thread, event callback, refcount, timeout poller, media-event pool, and claim pointer.
- `lba_range` is used for compare-and-write emulation, quiesce, and range locking; this chunk declares lock/unlock helpers but their main implementation continues in chunk 2.

## Initialization, Examine, And Shutdown

- `spdk_bdev_initialize()` registers notify types, registers the bdev iobuf module, creates the global `spdk_bdev_io` mempool sized as `sizeof(struct spdk_bdev_io) + max module ctx`, allocates the zero buffer, registers the manager io_device, and initializes every registered bdev module.
- Module init/examine progress is tracked with each module's `internal.action_in_progress`; async module init and examine callbacks must call `spdk_bdev_module_init_done()` or `spdk_bdev_module_examine_done()`. `bdev_module_action_complete()` only calls the user init callback once all actions are complete.
- `bdev_examine()` runs `examine_config()` for all modules, then `examine_disk()` depending on claim state: all modules for unclaimed bdevs, the v1 claiming module for `SPDK_BDEV_CLAIM_EXCL_WRITE`, or every v2 claimant module. It carefully drops the bdev spinlock around module callbacks and defers cleanup of v2 claims released during examine.
- Manual examine is allowed only when `bdev_auto_examine` is false. Names are kept in `g_bdev_examine_allowlist`; matching aliases also qualify.
- `spdk_bdev_finish()` cancels async opens, waits for examine completion, calls module `fini_start`, unregisters bdevs top-down/reverse order, finalizes modules in reverse order, unregisters the manager io_device, frees the mempool/zero buffer/allowlist, and clears init flags.

## I/O Allocation, Buffers, Memory Domains, DIF, And Accel

- `bdev_channel_get_io()` pulls from the per-thread cache before the global mempool, and refuses to skip queued waiters. `spdk_bdev_free_io()` returns to the cache or mempool and drains `io_wait_queue` callbacks when cached entries become available.
- `spdk_bdev_io_get_buf()` uses caller buffers when present and aligned; otherwise it allocates from `spdk_iobuf`. Required length accounts for alignment padding and separate metadata.
- Bounce-buffer paths preserve original iovs/md buffers, replace the submitted iov with an aligned buffer, and copy/pull/write-side data before submit or push/read-side data after completion. Memory-domain pull/push is asynchronous and tracked on `io_memory_domain`.
- DIF metadata hiding is centralized in `bdev_io_needs_metadata()`, `bdev_io_init_dif_ctx()`, and accel sequence append operations. Interleaved metadata with hidden metadata or NVMe PRACT can trigger DIF generate/verify copy; separate metadata requires explicit md buffers and rejects unsupported PRACT/sequence combinations.
- Accel sequences are passed through only if the bdev module supports the I/O type and the I/O is not split. Otherwise, the bdev layer executes or amends the sequence before submit for writes and after data return for reads.

## Submission, Retry, QoS, Splitting, And Locks

- Public APIs allocate/init `spdk_bdev_io`, fill type-specific unions, then call `_bdev_io_submit_ext()` or `bdev_io_submit()`. Common validation includes descriptor write permission, block-range overflow/limit checks, feature support bitmasks, block-byte divisibility, metadata layout constraints, and `-ENOMEM` on I/O allocation failure.
- `bdev_io_submit()` first checks channel locked ranges for non-child I/Os, adds the I/O to `io_submitted`, records trace start and submit timestamp, then either starts split handling or calls `_bdev_io_submit()`.
- `_bdev_io_submit()` handles reset-in-progress aborts, QoS queuing, and normal submission. `bdev_io_do_submit()` handles queued abort targets, write-unit constraints, NOMEM backpressure, outstanding counters, and backend `fn_table->submit_request()`.
- NOMEM retry is ordered through `shared_resource->nomem_io` with explicit retry states: submit, pull/pull-md, push/push-md, and accel-buffer acquisition. Threshold logic waits for outstanding I/O to drain; a poller covers the qd=1/no-outstanding corner case.
- QoS supports RW IOPS, RW BPS, read BPS, and write BPS limits with atomic per-timeslice quota. One channel is selected as the QoS channel; all channels get `BDEV_CH_QOS_ENABLED` and queued I/Os are retried from the QoS poller.
- Split logic handles READ/WRITE by boundary, max segment count/size, max I/O size, and write-unit/optimal boundaries; UNMAP, WRITE_ZEROES, and COPY split by their max limits and cap child submissions per round. Parent completion waits on `split.outstanding`, propagates child error status, then performs any required parent-level accel/bounce completion.
- LBA range locking is visible in `bdev_io_range_is_locked()` and compare-and-write emulation. Reads are only blocked for quiesce ranges, while writes/unmap/write-zeroes/zcopy/copy are blocked on overlap unless they belong to the lock owner channel/context.

## Public API Surface Covered

- Discovery/config: `spdk_bdev_get_by_name()`, bdev iteration including leaf-only iteration, option get/set, `spdk_bdev_subsystem_config_json()`, manual examine, wait-for-examine.
- Descriptor/channel metadata: `spdk_bdev_get_io_channel()`, module/name/product/alias/block-size/getter family, metadata/DIF getters, NVMe namespace/csi/ctratt getters, QoS limit getters.
- I/O APIs: read/readv/readv_ext, write/writev/writev_ext, compare, compare-and-write, zcopy start/end, write zeroes with write emulation, write uncorrectable, unmap, flush, reset, NVMe NSSR, NVMe admin/io/io-md/iov-md passthrough, seek data/hole fallback, abort by callback arg, queue wait.
- Stats/telemetry: per-channel and device stat aggregation/reset, JSON stat dump, queue-depth sampling/current QD, resize notification, histogram enable config serialization, trace records, optional VTune metadata.
- Completion/status: `spdk_bdev_io_complete()`, SCSI/AIO/NVMe/base status setters/getters, fused NVMe status mapping, statistics update, histogram tally, deferred completion when backend completes during submit.

## Registration, Unregistration, And Open

- `bdev_register()` validates name, allocates internal stats, initializes internal lists/status/claims, generates UUID if needed, adds UUID alias, snapshots supported I/O and accel-sequence bitmasks from the module, detects memory-domain support, fills defaults (`write_unit_size`, `acwu`, `phys_blocklen`, `max_copy`, emulated `max_write_zeroes`), registers the bdev io_device, inserts the canonical name into the global RB tree, and finally appends to `g_bdev_mgr.bdevs`.
- `spdk_bdev_unregister()` transitions status through UNREGISTERING/REMOVING, stops QD sampling, aborts queued channel I/O, rejects duplicate unregisters, hot-remove notifies open descriptors, handles QoS destruction races, removes names/aliases/allowlist entries, and unregisters the io_device once no descriptors or reset/range locks block destruction.
- `bdev_open()` requires an SPDK thread, rejects removing devices, rejects write opens on claimed bdevs, starts QoS if configured, and links the descriptor. `spdk_bdev_open_ext_v2()` holds the global manager spinlock during lookup/open.
- The chunk ends in `spdk_bdev_open_async()`. Adjacent context shows it allocates an async context, duplicates the name, registers a 100 ms poller, stores callbacks/options/original thread, queues in `g_bdev_mgr.async_bdev_opens`, and attempts an immediate open. Its close/destructor interactions continue in chunk 2.

## Dependencies

- SPDK core: `spdk/thread.h`, io_device/channels, pollers/messages, spinlocks, mempools, iobuf, notify, trace, JSON, UUID, logging, env allocation.
- Data movement/protection: `spdk/accel.h`, `spdk/dma.h`, memory domains, DIF helpers, NVMe/SCSI specs and status translation.
- Backend contract: every `struct spdk_bdev` depends on its module `fn_table` for `submit_request`, `get_io_channel`, feature support, optional accel/memory-domain support, config/info JSON, destruct, and optional spin-time metrics.

## Risks And Invariants

- Lock ordering is delicate: global manager spinlock and bdev internal spinlock are both used, while module callbacks/examine paths intentionally drop bdev locks.
- Completion assumes strict ownership: submitted I/Os must be on `io_submitted`; unsubmitted failure paths must use `bdev_io_complete_unsubmitted()`.
- Outstanding counters must stay balanced across backend submit, accel execution, memory-domain transfer, reset freeze/unfreeze, and queued abort paths.
- Async memory-domain and accel operations cannot be forcibly aborted; reset may fail if those queues remain active after drain timeout.
- QoS teardown swaps structures because new opens/channels can race with async poller destruction.
- The bdev name RB tree is the public lookup gate; `bdev_register()` intentionally exposes the name only after io_device and internal state are ready.
- Manual compare-and-write emulation relies on LBA locking; the actual range lock/unlock implementation is outside this chunk, so correctness depends on chunk 2.

## Cross-Chunk References

- Lines after 9156 complete `spdk_bdev_open_async()`, then implement descriptor close, media event queueing, module/claim APIs, QoS setters, histogram APIs, memory-domain query wrappers, LBA lock/unlock/quiesce internals, `spdk_bdev_for_each_io()`, and log/trace registration.
- Forward declarations in this chunk whose definitions continue later include `bdev_enable_qos_msg()`, `bdev_enable_qos_done()`, `bdev_lock_lba_range()`, `bdev_unlock_lba_range()`, `claim_type_is_v2()`, `bdev_desc_release_claims()`, `claim_reset()`, and `bdev_write_zero_buffer()`.

### Chunk 2: lines 9157-11549

# Chunk Research: sources/virtualization/spdk/lib/bdev/bdev.c lines 9157-11549

## Scope

This chunk covers the tail of asynchronous bdev open, descriptor close and registration completion, bdev claim APIs including v1 exclusive claims and v2 multi-claim modes, bdev iteration helpers, bdev I/O metadata accessors, module registration, zero-fill fallback writes, QoS rate-limit enable/update/disable orchestration, histogram control and collection, media-management event queues, LBA-range locking and module quiesce/unquiesce, memory-domain queries, channel/I/O iteration wrappers, copy-blocks emulation, and bdev tracepoint registration.

The first line continues `_bdev_open_async()` from the previous chunk: open attempts, timeout checks, async-open shutdown cancellation, and `struct spdk_bdev_open_async_ctx` are defined just before this range. Many low-level helpers used here, including I/O submission, block-range validation, LBA overlap checks, QoS poller setup/destruction, and `set_qos_limit_ctx`, are also defined earlier in `bdev.c`.

## APIs And Entry Points

- Async open: `spdk_bdev_open_async()`, `bdev_open_async()`, option default/copy helpers.
- Close/register: `spdk_bdev_close()`, internal `bdev_close()`, `spdk_bdev_register()`, and `bdev_register_finished()`.
- Claims: legacy `spdk_bdev_module_claim_bdev()` plus v2 `spdk_bdev_module_claim_bdev_desc()` modes.
- Enumeration: `spdk_for_each_bdev()`, `spdk_for_each_bdev_leaf()`, `spdk_for_each_bdev_by_name()`.
- QoS/histograms/media events: rate-limit changes, per-channel histogram allocation/merge/free, descriptor media-event queues.
- LBA locks/quiesce: global and per-channel range locking plus module-scoped quiesce/unquiesce.
- Copy/tracing: `spdk_bdev_copy_blocks()` native-or-emulated copy and `bdev_trace()` tracepoint registration.

## Control Flow

Async open allocates a context, registers a 100 ms poller, queues it under `g_bdev_mgr.spinlock`, and immediately attempts open. Completion unregisters the poller, removes the async-open queue entry, and sends the callback to the originating thread.

Close removes a descriptor from `open_descs`, marks it closed, releases claims, frees it when refs reach zero, destroys QoS on last close, and may finish deferred unregister for a removing bdev.

Claim verification is mode-specific: read-write-once rejects existing claims and other writers; read-only-many requires non-writable descriptors; read-write-shared requires a nonzero matching shared key. Successful v2 claims allocate `spdk_bdev_module_claim`, link it into `claim.v2.claims`, and may promote the descriptor to writable.

QoS changes are serialized by `qos_mod_in_progress`. Limits are normalized in place, enabling walks channels to set QoS, updating posts to the QoS thread, and disabling clears per-channel QoS flags, resubmits queued I/O, then frees QoS state on the owning thread.

Histogram enable/disable is serialized by `histogram_in_progress`; enable allocates per-channel histograms and rolls back partial allocations on failure, while get merges all channel histograms into the caller aggregate.

LBA locking inserts a global lock range or pending range, installs per-channel copies, polls until overlapping submitted I/O drains, then lets matching owner-channel/caller-context I/O proceed. Unlock removes the global range first, removes channel copies, resubmits locked I/O, promotes pending ranges, and may resume unregister.

Copy-blocks validates writable descriptor and source/destination ranges. It submits native/split copy when available; otherwise it allocates a buffer and performs read-then-write emulation, queuing retry callbacks on `-ENOMEM`.

## State And Dependencies

Global state: `g_bdev_mgr.spinlock`, `async_bdev_opens`, `bdev_modules`, `zero_buffer`.

Per-bdev state: `open_descs`, `status`, `qos`, `qos_mod_in_progress`, claim fields, `examine_in_progress`, histogram fields, `locked_ranges`, `pending_locked_ranges`.

Per-descriptor/channel state: descriptor refs/write/claim/media queues; channel `locked_ranges`, `io_locked`, `io_submitted`, `qos_queued_io`, flags, histogram.

Dependencies include SPDK threads/pollers, spinlocks, TAILQ, bdev open/register/unregister/examine helpers, channel iteration, histogram APIs, bdev function-table callbacks, QoS helpers, event notification, I/O submission/range validation, and trace registration.

## Risks And Cross-Chunk References

- The chunk starts mid async-open completion; shutdown cancellation and timeout logic are in the prior chunk.
- V2 claim release during examination leaves dead claim nodes for later cleanup outside this chunk.
- `spdk_bdev_set_qos_rate_limits()` mutates the caller-provided `limits` array.
- QoS teardown is lifetime-sensitive because channel iteration and final free can occur on different threads.
- Histogram state fields are written after dropping the spinlock once `histogram_in_progress` is set.
- Media-event push targets the first writable descriptor with a buffer and can short-count/drop events.
- LBA lock correctness depends on earlier `bdev_io_range_is_locked()` and `bdev_lba_range_overlapped()`.
- Unlock resubmits all `io_locked` entries and depends on `bdev_io_submit()` rechecking remaining locks.
- Copy emulation can allocate `num_blocks * block_size`; large copies rely on native copy or split logic.
- Trace relations reference NVMe/blob/RAID tracepoints defined elsewhere.

## Summary

This chunk is the public-control and coordination tail of SPDK bdev: close/register, descriptor claims, iteration, QoS, histograms, media events, LBA quiesce/locking, memory-domain access, copy emulation, and tracing. The highest-risk areas are descriptor/bdev lifetime, claim cleanup during examination, cross-thread QoS/histogram changes, and range-lock interaction with submitted and locked I/O queues.

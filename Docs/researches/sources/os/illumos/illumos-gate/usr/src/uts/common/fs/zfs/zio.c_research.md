# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/zio.c

## Purpose

`zio.c` is the central ZFS I/O pipeline implementation. It creates, schedules, transforms, verifies, retries, completes, and destroys `zio_t` operations for logical block reads/writes, physical vdev I/O, frees, claims, trims, cache flushes, dedup paths, gang blocks, encryption, checksums, and error recovery.

## Major Responsibilities

- Initializes and destroys ZIO object/link/buffer kmem caches through `zio_init()` and `zio_fini()`.
- Provides metadata/data buffer allocation helpers:
  - `zio_buf_alloc()`, `zio_buf_free()`
  - `zio_data_buf_alloc()`, `zio_data_buf_free()`
- Maintains transform stacks used for compression, decompression, encryption, decryption, subblock expansion, and embedded/physical buffer conversions.
- Manages parent/child relationships, wait states, child error propagation, and pipeline stalls.
- Constructs public ZIO types:
  - `zio_root()`, `zio_null()`
  - `zio_read()`, `zio_write()`, `zio_rewrite()`
  - `zio_free()`, `zio_free_sync()`
  - `zio_claim()`
  - `zio_ioctl()`, `zio_trim()`
  - `zio_read_phys()`, `zio_write_phys()`
  - `zio_vdev_child_io()`, `zio_vdev_delegated_io()`
- Implements the staged pipeline executor `zio_execute()`, synchronous wait path `zio_wait()`, and async submission path `zio_nowait()`.
- Handles retry, suspend, resume, reexecution, failure-mode escalation, and FMA ereport posting.
- Implements gang block assembly/issue/write/failure rollback.
- Implements dedup table read/write/free coordination.
- Allocates, frees, claims, unallocates, and throttles DVAs.
- Issues I/O into vdev queues and handles completion/assessment.
- Calls encryption, checksum generation, checksum verification, and completion callbacks.
- Provides bookmark ordering helpers used by scan/traversal logic.

## Pipeline Model

`zio_execute()` advances `zio->io_stage` through `zio->io_pipeline` until the operation completes, blocks on children, is dispatched to another taskq, waits for device interrupt, is queued/delegated, or reaches `zio_done()`.

The pipeline table is:

- `zio_read_bp_init`
- `zio_write_bp_init`
- `zio_free_bp_init`
- `zio_issue_async`
- `zio_write_compress`
- `zio_encrypt`
- `zio_checksum_generate`
- `zio_nop_write`
- `zio_ddt_read_start`
- `zio_ddt_read_done`
- `zio_ddt_write`
- `zio_ddt_free`
- `zio_gang_assemble`
- `zio_gang_issue`
- `zio_dva_throttle`
- `zio_dva_allocate`
- `zio_dva_free`
- `zio_dva_claim`
- `zio_ready`
- `zio_vdev_io_start`
- `zio_vdev_io_done`
- `zio_vdev_io_assess`
- `zio_checksum_verify`
- `zio_done`

Pipeline interlocks are explicit: `zio_wait_for_children()` rewinds the stage and stores a stall pointer to a child counter. When the last child reaches the waited state, `zio_notify_parent()` redispatches the parent on the appropriate taskq.

## Transform Handling

`zio_push_transform()` replaces `io_abd` and `io_size` with transformed data while saving the original ABD/size and an optional callback. `zio_pop_transforms()` unwinds in LIFO order, optionally calls the transform callback, frees temporary ABDs, and restores original data.

Important transform callbacks:

- `zio_subblock()` copies read data out of a larger physical block.
- `zio_decompress()` expands compressed data after successful reads.
- `zio_decrypt()` authenticates/decrypts protected reads and logs authentication failures.

This stack lets write stages compress/encrypt before vdev I/O while restoring the caller-facing buffer at completion.

## Read Path

`zio_read()` verifies the block pointer and creates a logical read pipeline. `zio_read_bp_init()` configures transforms and special cases:

- Compressed logical reads push a decompression transform unless `ZIO_FLAG_RAW_COMPRESS` is set.
- Protected logical reads push a decryption/authentication transform unless `ZIO_FLAG_RAW_ENCRYPT` is set.
- Embedded data block pointers are decoded directly and switch to the interlock pipeline.
- Metadata/user-data cache flags are adjusted.
- Dedup blocks switch to the DDT read pipeline.
- Gang blocks add gang stages.

Checksum verification occurs near the vdev side. For vdev child reads with a block pointer, `zio_vdev_child_io()` can move checksum verification down to children, closer to leaf devices.

## Write Path

`zio_write()` validates `zio_prop_t`, creates a logical write, stores callbacks, and disables dedup when required data is unavailable for dedup verification or encrypted dedup.

`zio_write_bp_init()` handles override block pointers, nopwrite state, and DDT eligibility.

`zio_write_compress()` waits for logical/gang children, runs `io_children_ready`, compresses unless disabled by sync convergence policy, handles embedded data blocks, rounds compressed physical size to ashift, checks zero blocks, chooses rewrite vs allocate pipeline, and fills `blkptr_t` fields. It can switch to DDT or nopwrite paths.

`zio_encrypt()` handles protected writes after compression and before checksum generation. It supports raw encrypted writes, authenticated-only block types, indirect MAC checksums, objset MACs, ZIL MAC handling, and full data encryption through SPA crypto helpers.

`zio_checksum_generate()` computes the final checksum or embedded checksum after encryption.

## Free and Claim Paths

`zio_free()` validates the block pointer and either ignores embedded frees, defers frees to a bplist, or immediately waits on `zio_free_sync()`. Deferral depends on gang/dedup status, syncing txg, sync pass, and log spacemap feature state.

`zio_free_sync()` creates free pipeline work and may add async issue when gang or dedup blocks require reads.

`zio_claim()` is used during intent log replay/import to claim already-written blocks before new allocations can collide. Embedded blocks become null ZIOs. Dedup claims are only asserted for non-writable/zdb contexts.

## Parent/Child Accounting

`zio_add_child()` links parent and child with `zio_link_t`, increments per-child-type wait counters for all states the child has not reached, and enforces child-type hierarchy.

`zio_notify_parent()` propagates worst child error unless suppressed, propagates reexecute intent, decrements wait counters, and redispatches stalled parents when counters reach zero.

Errors are inherited by child class in `zio_done()` through `zio_inherit_child_errors()` in a controlled order.

## Gang Blocks

Gang blocks are represented as an in-core `zio_gang_node_t` tree of gang headers. The code uses a two-phase model:

- `zio_gang_assemble()` recursively reads gang headers into `io_gang_tree`.
- `zio_gang_issue()` walks the assembled tree and issues read/rewrite/free/claim children.

This avoids partial free/claim/write operations before all headers are known. If a gang write fails, `zio_dva_unallocate()` walks the gang tree and frees allocations immediately.

`zio_write_gang_block()` allocates a gang header, writes it, splits the data into up to `SPA_GBH_NBLKPTRS` members, and recursively creates gang child writes. Encrypted gang headers reserve DVA space for crypto metadata and cannot use all three copies.

## Dedup

DDT logic is embedded in staged handlers:

- `zio_ddt_read_start()` reads dedup blocks or starts repair reads from alternate DDT phys entries.
- `zio_ddt_read_done()` waits for repair children, copies repaired data if found, and closes the DDT repair state.
- `zio_ddt_collision()` verifies dedup collisions by comparing in-flight lead writes or existing on-disk data.
- `zio_ddt_write()` inserts or references DDT entries, creates lead writes, handles ditto copies, and downgrades to normal writes or stronger checksums on verified collision.
- `zio_ddt_free()` decrements DDT refcounts.

Dedup write children share transformed data through pushed transforms rather than recomputing compression/encryption.

## DVA Allocation and Throttling

`zio_dva_throttle()` chooses an allocation class with `spa_preferred_class()`, hashes the bookmark to an allocator lane, queues async writes in per-allocator AVL trees, and reserves allocation slots through metaslab throttle logic.

`zio_dva_allocate()` performs metaslab allocation, falls back from special allocation class to normal class on `ENOSPC`, and falls back to gang block allocation when large allocations fail.

`zio_dva_free()` and `zio_dva_claim()` call metaslab free/claim helpers.

`zio_alloc_zil()` separately allocates ZIL blocks, preferring log class and falling back to normal class. It fills block pointer fields and pre-generates encryption salt/IV for encrypted ZIL blocks.

## Vdev I/O

`zio_vdev_io_start()` handles top-level mirror dispatch when no concrete vdev is set, alignment expansion for logical I/O, repair bypass for non-dirty DTL regions, vdev cache reads/writes, vdev queueing, accessibility checks, delay timing, and dispatch to `vdev_op_io_start`.

`zio_vdev_io_done()` waits for vdev children, completes vdev queue accounting, updates vdev cache for writes, applies device/label fault injection, converts inaccessible-device errors to `ENXIO`, calls `vdev_op_io_done`, and probes unexpected leaf errors.

`zio_vdev_io_assess()` releases config locks, frees vdev-specific data, applies logical fault injection, retries eligible top-level failures, marks non-leaf vdevs unable to write on `ENXIO`, remembers unsupported write-cache flushes, invokes physical done callbacks, and short-circuits on errors.

## Completion and Error Recovery

`zio_ready()` marks the ready state, calls ready callbacks, updates block pointer copies, releases allocation throttle reservations on early failure, notifies ready-waiting parents, handles nodata gang exceptions, and can invoke ignored-write injection.

`zio_done()` is the main finalizer. It waits for all children, updates allocation throttle accounting, validates block pointer invariants, inherits child errors, finishes checksum reports, pops transforms, updates vdev stats, posts slow I/O and error ereports, decides reexecution/suspend policy, rolls back failed allocations, frees gang trees, calls done callbacks, notifies parents, wakes synchronous waiters, or destroys async ZIOs.

Reexecution is top-down. Failed logical roots can reexecute immediately on a taskq or suspend under `spa_suspend_zio_root` until `zio_resume()` reruns them.

## Bookmark Helpers

`zio_bookmark_compare()` orders live ZIOs by bookmark and pointer address.

`zbookmark_compare()` canonicalizes meta-dnode bookmarks so traversal ordering works across meta-dnode and normal-object references.

`zbookmark_subtree_completed()` checks whether a level-0 last-visited bookmark implies completion of a subtree.

## Key Dependencies

- ABD buffer API for scatter/gather data movement.
- ARC for reads and freed-block notification.
- SPA/vdev/metaslab layers for config, taskqs, allocation, device I/O, and stats.
- DDT for dedup.
- ZIO checksum, compression, and crypt modules.
- FMA/ZFS ereport helpers.
- Fault injection from `zio_inject.c`.

## Notes for Future Readers

- `io_pipeline`, `io_stage`, and child wait counters are tightly coupled. Any new stage must preserve stall/redispatch semantics.
- Transform callbacks may set `io_error` while unwinding in `zio_done()`.
- Encryption, checksum, and compression order is deliberate: write path compresses, encrypts, then checksums ciphertext; read path verifies then decrypts/decompresses through transforms.
- Gang and dedup children intentionally alter normal parent/child propagation rules.
- `ZIO_FLAG_DONT_PROPAGATE`, `ZIO_FLAG_IO_RETRY`, `ZIO_FLAG_CANFAIL`, and `ZIO_FLAG_SPECULATIVE` materially change visible error behavior.

# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/arc.c

This report was synthesized from ordered chunk research outputs.

## Chunk Map

- chunk 1: lines 1-8413, source bytes 262128, report `Docs/researches/chunks/chunk_sources_os_illumos_illumos_gate_usr_src_uts_common_fs_zfs_arc_c_1_1_8413_77d747229b5c_research.md`
- chunk 2: lines 8414-10052, source bytes 49975, report `Docs/researches/chunks/chunk_sources_os_illumos_illumos_gate_usr_src_uts_common_fs_zfs_arc_c_2_8414_1_814f185db0d5_research.md`

## Chunk Research

### Chunk 1: lines 1-8413

# Chunk Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/arc.c lines 1-8413

## Scope

This chunk covers the illumos ZFS ARC implementation from the file header through the beginning of L2ARC write-side data transforms. It includes the ARC theory comments, locking model, core tunables and kstats, DVA/birth keyed hash table, L1 ARC header/buffer lifecycle, compressed and encrypted buffer handling, ARC state transitions, eviction/reclaim, read/write entry points, dirty-data throttling, ARC initialization/finalization, and early L2ARC read/write/eviction support.

The chunk ends inside `l2arc_apply_transforms()` after allocating a compressed-data ABD and borrowing a temporary buffer. The rest of L2ARC write transforms, feed/write loops, device management, rebuild logic, and module teardown/tunable registration are outside this chunk.

## APIs And Entry Points

- Public ARC inspection/transform APIs: `arc_buf_size()`, `arc_buf_lsize()`, `arc_is_encrypted()`, `arc_is_unauthenticated()`, `arc_get_raw_params()`, `arc_get_compression()`, `arc_is_metadata()`, `arc_buf_thaw()`, `arc_buf_freeze()`, and `arc_untransform()`.
- Public buffer allocation and loan APIs: `arc_alloc_buf()`, `arc_alloc_compressed_buf()`, `arc_alloc_raw_buf()`, `arc_buf_alloc_l2only()`, `arc_loan_buf()`, `arc_loan_compressed_buf()`, `arc_loan_raw_buf()`, `arc_return_buf()`, and `arc_loan_inuse_buf()`.
- Public lifetime/mutation APIs: `arc_buf_destroy()`, `arc_freed()`, `arc_release()`, `arc_released()`, and debug-only `arc_referenced()`.
- Public I/O APIs: `arc_read()`, `arc_bcopy_func()`, `arc_getbuf_func()`, and `arc_write()`.
- Public memory/cache APIs: `arc_flush()`, `arc_memory_is_low()`, `arc_tempreserve_space()`, `arc_tempreserve_clear()`, `arc_max_bytes()`, `arc_init()`, and `arc_fini()`.

## State And Control Flow

- ARC identity is `(spa load guid, BP identity DVA, physical birth)`, stored in `buf_hash_table` with striped mutexes and CityHash indexing.
- Six ARC states are initialized: `arc_anon`, `arc_mru`, `arc_mru_ghost`, `arc_mfu`, `arc_mfu_ghost`, and `arc_l2c_only`, each with metadata/data multilists and size/evictable refcounts.
- `arc_buf_hdr_t` is the authoritative cache header; `arc_buf_t` is the consumer-visible buffer. Multiple buffers can share a header, and some may share the header’s linear ABD data when flags and ordering invariants allow it.
- `arc_buf_fill()` handles authentication, decryption, dnode in-place decryption, decompression, copying, byteswapping, and debug checksums.
- `arc_change_state()`, `add_reference()`, and `remove_reference()` coordinate state transitions, hash/list membership, L2ARC stats, and active versus evictable accounting.
- `arc_evict_hdr()`, `arc_evict_state()`, and `arc_adjust()` implement MRU/MFU eviction, ghost transitions, L2-only compaction, metadata/data balancing, and overflow waiter wakeups.
- `arc_read()` handles L1 hits, in-flight read joins, ghost/L2-only rehydration, optional L2ARC reads, and fallback `zio_read()`. `arc_read_done()` completes callbacks, handles transform errors, clears I/O state, and wakes waiters.
- `arc_write()` prepares raw/compressed/encrypted ZIO properties, detaches stale header data, and issues `zio_write()`. `arc_write_ready()` repopulates header data; `arc_write_done()` assigns final DVA/birth identity and inserts successful writes.
- `arc_release()` anonymizes a buffer before modification, either reusing a single-buffer header or splitting it into a new anonymous header.
- L2ARC logic covered here includes eligibility, write size/interval calculation, device rotation, write completion, read validation/fallback, sublist priority, log-block overhead, device-region eviction, and the start of write transforms.

## Dependencies

- ZFS SPA/vdev/ZIO, blkptr/DVA macros, checksum/compression, ABD, DMU byteswap/object types, DSL dirty-data accounting, ZIL MAC decoding, and ZFS ereports.
- Crypto helpers including `spa_do_crypt_abd()`, `spa_do_crypt_mac_abd()`, `spa_do_crypt_objset_mac_abd()`, `zio_crypt_decode_*()`, and later `dsl_crypto_key_t` use.
- illumos VM and kernel state: `physmem`, `freemem`, `needfree`, `lotsfree`, `desfree`, `availrmem`, `swapfs_minfree`, `pages_pp_maximum`, `heap_arena`, `zio_arena`, DNLC, kmem/vmem reaping, zthreads, kstats, multilists, refcounts, atomics, and DTrace.
- L2ARC device/log-block structures, vdev space accounting, SCL_L2ARC config locks, and persistence helpers declared here but mostly implemented later.

## Risks And Cross-Chunk References

- Header flags require the hash lock or an undiscoverable header; violating this can race lookup, eviction, read completion, or L2ARC updates.
- L2ARC paths intentionally use `mutex_tryenter()` to avoid hash-lock/`l2ad_mtx` deadlocks.
- Shared buffer accounting is fragile across `arc_share_buf()`, `arc_unshare_buf()`, `arc_buf_destroy_impl()`, `arc_release()`, and `arc_write()`.
- Eviction is best-effort and may not reclaim enough due to references, I/O, lock misses, prefetch lifetimes, or L2ARC writes.
- L2ARC hits are trusted only after checksum validation against the original BP; failures must fall back to primary storage.
- The chunk ends mid-`l2arc_apply_transforms()`. Chunk 2 must verify recompression/encryption behavior, cleanup paths, `abd_out` ownership, L2ARC feed/write loops, persistence rebuild helpers, device lifecycle, and final module plumbing.

### Chunk 2: lines 8414-10052

# Chunk Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/arc.c lines 8414-10052

## Scope

This chunk covers illumos ZFS L2ARC write selection, feed-thread control, cache-device lifecycle, persistent L2ARC rebuild, log-block read/write/restore helpers, and rotary address validation. It starts mid-`l2arc_apply_transforms()`, so the earlier transform-entry decisions are in the previous chunk.

## APIs And Entry Points

- `l2arc_apply_transforms()` prepares aligned ABDs for L2ARC writes, including compression, encryption, padding, MAC verification, and cleanup on key/crypto failure.
- `l2arc_write_buffers()` scans ARC lists, selects eligible headers, writes buffers to an L2ARC vdev, logs persistent metadata, waits for write completion, and updates the device header.
- `l2arc_feed_thread()` periodically chooses an L2ARC device, evicts the overwrite range, writes buffers, and schedules the next feed.
- Device lifecycle: `l2arc_vdev_present()`, `l2arc_vdev_get()`, `l2arc_add_vdev()`, `l2arc_rebuild_vdev()`, `l2arc_remove_vdev()`.
- Subsystem lifecycle: `l2arc_init()`, `l2arc_fini()`, `l2arc_start()`, `l2arc_stop()`.
- Persistent rebuild: `l2arc_spa_rebuild_start()`, `l2arc_dev_rebuild_start()`, `l2arc_rebuild()`.
- Metadata I/O and restore helpers: `l2arc_dev_hdr_read()`, `l2arc_log_blk_read()`, `l2arc_log_blk_fetch()`, `l2arc_log_blk_fetch_abort()`, `l2arc_dev_hdr_update()`, `l2arc_log_blk_restore()`, `l2arc_hdr_restore()`, `l2arc_log_blk_commit()`, `l2arc_log_blkptr_valid()`, `l2arc_log_blk_insert()`, `l2arc_range_check_overlap()`.

## Control Flow

`l2arc_write_buffers()` iterates feed passes, optionally skipping MRU passes under `l2arc_mfuonly`. It locks ARC multilists, scans from head during cold ARC warmup and tail after warmup, bounds scan depth by headroom, uses `mutex_tryenter(HDR_LOCK())`, skips ineligible headers, marks chosen headers with `ARC_FLAG_L2_WRITING`, chooses either raw ABD, live ARC ABD, or transformed copy, then issues `zio_write_phys()` writes under one root zio.

The first selected write installs a dummy list marker for `l2arc_write_done()` cleanup. Each header gets `b_l2hdr` metadata, is inserted into `l2ad_buflist`, increments allocation refcounts, advances `l2ad_hand`, updates stats/vdev accounting, and is appended to the persistent log block. Full log blocks are committed immediately. If nothing is written, the dummy header is freed and the device header is updated only if eviction moved.

`l2arc_feed_thread()` waits on a timed CV, skips when no devices exist, obtains a device and spa config lock via `l2arc_dev_get_next()`, skips read-only pools, aborts on L2 header pressure, computes write size, calls `l2arc_evict()`, writes buffers, computes the next interval, and exits by resetting `l2arc_thread_exit`.

`l2arc_add_vdev()` allocates `l2arc_dev_t`, reserves label/header space, initializes hand/evict pointers, lists, refcounts, and device-header storage, publishes the device globally, and calls `l2arc_rebuild_vdev()`. `l2arc_rebuild_vdev()` computes log-entry count, reads the persistent device header, marks rebuild pending when valid, or writes a fresh zeroed header for writable pools.

`l2arc_rebuild()` restores hand/evict/first-pass state from the header, walks the persistent log-block chain with lookahead I/O, validates checksums/compression/magic, aborts under memory pressure, drops `SCL_L2ARC` while restoring headers, handles cancellation while reacquiring the config lock, records restored log-block pointers, and logs disabled/success/no-valid-blocks/canceled/aborted outcomes.

`l2arc_log_blk_restore()` restores entries in reverse order to preserve temporal ordering. `l2arc_hdr_restore()` allocates L2-only ARC headers, inserts them into device lists/refcounts, and handles duplicate cached headers by attaching missing L2 metadata to the existing header.

`l2arc_log_blk_commit()` serializes a full in-memory log block, links it into the previous-chain pointer, optionally LZ4-compresses it, updates `dh_start_lbps`, computes Fletcher-4, writes it at `l2ad_hand`, records the pointer/refcounts/stats, and resets log-block assembly fields.

## State And Dependencies

Key global state includes `l2arc_dev_list`, `l2arc_ndev`, `l2arc_dev_last`, `l2arc_thread_exit`, feed/rebuild locks and CVs, `l2arc_free_on_write`, `arc_warm`, `arc_c`, `arc_c_max`, `arc_meta_limit`, `astat_l2_hdr_size`, and tunables such as `l2arc_headroom`, `l2arc_meta_percent`, `l2arc_feed_secs`, and `l2arc_rebuild_enabled`.

Per-device state includes `l2ad_spa`, `l2ad_vdev`, `l2ad_start/end/hand/evict`, `l2ad_first`, `l2ad_writing`, rebuild flags, persistent header, buflist, log-block pointer list, log-block assembly fields, and allocation/log-block refcounts.

Dependencies include ARC header helpers, multilists, ABD APIs, ZIO physical I/O, SPA config locking, vdev accounting, compression/decompression, Fletcher checksums, byteswap helpers, DSL crypto key lookup/release, ABD encryption, zfs refcounts, kernel threads/CVs/mutexes, and ARC stat macros.

## Risks And Cross-Chunk References

- The chunk begins mid-`l2arc_apply_transforms()`; earlier copy/raw/shared-data decisions are in the previous chunk.
- `l2arc_write_buffers()` depends on earlier `l2arc_write_eligible()`, `l2arc_evict()`, `l2arc_write_done()`, and free-on-write ABD cleanup.
- `ARC_FLAG_L2_WRITING` is critical for header lifetime; completion must clear it on all success/failure paths.
- Direct ABD use is safe only when compression, encryption, sharing, and alignment flags are exactly right.
- Encrypted L2ARC writes intentionally skip buffers if the dataset key is unavailable.
- Rebuild drops `SCL_L2ARC` during header restoration, so cancellation/removal safety depends on rebuild locks and cancel flags.
- `l2arc_log_blkptr_valid()` and `l2arc_range_check_overlap()` are off-by-one-sensitive rotary-buffer checks.
- Restored L2-only headers are metadata; later ARC read paths must still validate DVA, birth, checksum, and transforms.

## Summary

This chunk is the illumos L2ARC operational core for writing cache-device data, persisting/restoring L2ARC metadata, managing cache vdev objects, and validating rotary log-block ranges. The highest-risk areas are asynchronous zio lifetime, ARC header locking, encryption/compression fidelity, rebuild cancellation, and wraparound address correctness.

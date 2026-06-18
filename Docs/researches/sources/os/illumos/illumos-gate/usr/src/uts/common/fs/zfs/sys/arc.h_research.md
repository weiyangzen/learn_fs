# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/arc.h

This header declares the ARC and L2ARC public interfaces, ARC buffer structures, flags, sizing macros, callbacks, memory accounting, read/write entry points, and lifecycle functions.

Key definitions:
- `ARC_EVICT_ALL` is used by `arc_flush()` to request eviction of all available buffers from a state.
- `HDR_SET_LSIZE()`, `HDR_SET_PSIZE()`, `HDR_GET_LSIZE()`, and `HDR_GET_PSIZE()` store/recover logical and physical sizes in units of `SPA_MINBLOCKSHIFT`.
- `arc_read_done_func_t` and `arc_write_done_func_t` define completion callbacks.
- Generic read callbacks `arc_bcopy_func` and `arc_getbuf_func` are declared.
- `arc_flags_t` includes public request flags (`WAIT`, `NOWAIT`, `PREFETCH`, `CACHED`, `L2CACHE`, predictive/prescient prefetch) and private header flags for hash membership, I/O state, errors, indirect blocks, async priority, L2ARC write/evict state, encryption/authentication, metadata, L1/L2 header presence, compressed ARC, shared data, and compression encoding bits.
- `arc_buf_flags_t` tracks shared, compressed, and encrypted arc buffers.
- `arc_buf_t` links to its header, next buffer, eviction lock, data pointer, and flags.
- `arc_buf_contents_t` distinguishes data and metadata buffers.
- `arc_space_type_t` classifies ARC memory accounting for data, metadata, headers, L2 headers, other, and bonus.
- `arc_state_type_t` names ARC states: anon, MRU, MRU ghost, MFU, MFU ghost, and L2-only.

Declared ARC operations:
- Memory accounting and metadata queries: `arc_space_consume()`, `arc_space_return()`, `arc_is_metadata()`, `arc_is_encrypted()`, `arc_is_unauthenticated()`, `arc_get_compression()`.
- Raw/encryption transforms: `arc_get_raw_params()`, `arc_untransform()`, `arc_convert_to_raw()`.
- Buffer allocation and loaning: normal, compressed, and raw variants for `arc_alloc_*` and `arc_loan_*`.
- Buffer lifetime/access: `arc_return_buf()`, `arc_loan_inuse_buf()`, `arc_buf_destroy()`, size queries, access marking, release/released checks, freeze/thaw, and debug reference query.
- I/O: `arc_read()` and `arc_write()` are the main cache read/write interfaces, with zio, spa, block pointer, callbacks, priority, flags, and bookmark context.
- Free notification: `arc_freed()`.
- Cache pressure and reservation: `arc_flush()`, `arc_tempreserve_clear()`, `arc_tempreserve_space()`.
- Memory status and lifecycle: `arc_memory_is_low()`, `arc_all_memory()`, `arc_max_bytes()`, `arc_init()`, `arc_fini()`.

Declared L2ARC operations:
- Device add/remove/presence/rebuild: `l2arc_add_vdev()`, `l2arc_remove_vdev()`, `l2arc_vdev_present()`, `l2arc_rebuild_vdev()`.
- Range overlap checking: `l2arc_range_check_overlap()`.
- Lifecycle and worker control: `l2arc_init()`, `l2arc_fini()`, `l2arc_start()`, `l2arc_stop()`, `l2arc_spa_rebuild_start()`.

Important notes:
- ARC callbacks explicitly allow transform/authentication errors independent of zio errors, especially for encrypted data.
- Userland builds expose `arc_watch` and `arc_procfd` for watchpoint support.

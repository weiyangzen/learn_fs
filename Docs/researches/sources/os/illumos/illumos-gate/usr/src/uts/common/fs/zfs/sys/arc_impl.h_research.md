# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/arc_impl.h

Read status: complete, 876 lines.

Purpose: private ARC/L2ARC implementation definitions. This header defines ARC state accounting, ARC callback records, split ARC buffer headers, persistent L2ARC on-disk metadata, L2ARC device state, encrypted-buffer header state, and the large ARC kstat surface.

Key structures and APIs:
- `arc_state_t` tracks per-state evictable lists and sizes for ARC data and metadata.
- `arc_callback_t` and `arc_write_callback_t` carry async read/write completion callbacks and associated ARC buffer state.
- `l1arc_buf_hdr_t`, `l2arc_buf_hdr_t`, `arc_buf_hdr_crypt_t`, and `arc_buf_hdr_t` define the memory-optimized ARC header layout, including L1-only, L2ARC-only, and encryption-specific fields.
- Persistent L2ARC metadata is described by `l2arc_dev_hdr_phys_t`, `l2arc_log_blkptr_t`, `l2arc_log_ent_phys_t`, and `l2arc_log_blk_phys_t`, with compile-time size/alignment checks.
- `l2arc_dev_t` stores per-cache-device write pointer state, persistent-log metadata, rebuild flags, and log-block accounting.
- `arc_stats_t` exposes ARC/L2ARC hit/miss, eviction, size, compression, rebuild, and memory-pressure counters.

Important implementation constraints:
- ARC buffers can live in anon, MRU, MFU, MRU ghost, MFU ghost, or L2ARC-only states; only unreferenced list-linked buffers can be evicted/deleted.
- Metadata and data are tracked separately for policy and accounting.
- L2ARC persistence depends on byte-order-aware magic values and packed property fields manipulated through bitfield macros.
- Several ARC sizing variables are aliases over kstat fields, avoiding duplicated shadow state.

Dependencies: `arc.h`, `multilist.h`, SPA/ZIO block and checksum definitions, ABD buffers, refcounts, kstats, and bitfield helpers.

Research notes:
- This is a central private ABI for `arc.c`, `zdb`, and L2ARC rebuild/write paths.
- The persistent L2ARC structs are on-disk format sensitive and guarded by `CTASSERT`.
- `l2arc_log_blkptr_valid()` is exported for `zdb.c`.

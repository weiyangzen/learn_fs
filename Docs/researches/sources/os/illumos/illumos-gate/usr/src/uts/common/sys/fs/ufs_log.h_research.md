# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/ufs_log.h

## Role

Defines UFS logging on-disk and in-core structures for LUFS: log extent mapping, circular buffers, on-disk log unit state, transaction maps, delta/map entries, cached roll buffers, roll buffers, statistics, debug flags, and log/map-layer prototypes.

## Key Structures

- `lufs_save_t` and `lufs_buf_t` support log buffer/save state.
- `extent_t`, `ic_extent_t`, `extent_block_t`, and `ic_extent_block_t` describe log space as extents.
- `cirbuf_t` manages read/write circular log buffers.
- `ml_odunit_t` is the sector-sized on-disk log unit state: version, badlog flag, transfer/device sizes, log bounds, requested/state/log sizes, state block, head/tail offsets and IDs, checksum, recovery transaction ID, debug bits, and timestamp.
- `ml_unit_t` is the in-core log unit with links, flags, buffer, ufsvfs backpointer, extents, delta/log/mata maps, reservation counters, transaction ID, read/write buffers, copied on-disk state, and locks.
- `sect_trailer_t` appends transaction/sector identity.
- `crb_t` is a cached roll buffer.
- `struct delta` records one metadata delta.
- `mapentry_t` stores a mapped delta with list/hash/age/cancel/roll links, callback, transaction ID, log offset, and flags.
- `mt_map_t` represents deltamap/logmap/matamap state, hash tables, commit/roll counters, synchronization primitives, roll thread coordination, and debug scan fields.
- `topstats_t`, `fio_lufs_stats_t`, `rollbuf_t`, `logstats`, and `threadtrans_t` provide stats and per-thread transaction accounting.

## Constants and Flags

Defines log sizing policy (`LDL_MINTRANSFER`, `LDL_MAXTRANSFER`, divisor, min/max log sizes), sector usable size, log version, log flags (`LDL_SCAN`, `LDL_ERROR`, `LDL_NOROLL`), map block geometry, mapentry flags, map types, map flags, overlap/within helpers, debug flags (`MT_*`), and stats structures.

## Interfaces

Declares log device layer, transaction driver layer, top layer, map layer, roll thread, and debug functions. The exported calls cover log strategy, commit/push/scan/head/tail management, buffer allocation, log enable/disable, delta/logmap insertion/removal, roll control, logscan, map get/put, and debug validation.

## Risk Notes

This header defines the logging subsystem’s persistent and in-core ABI. The on-disk log unit must fit in one sector. Map/list fields marked “MUST BE FIRST” are layout-sensitive for shared list handling.

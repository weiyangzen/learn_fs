# File Research: sources/virtualization/qemu/block/qed.h

Defines the QED on-disk format constants, feature bits, header layout, metadata table structures, L2 cache structures, request state, AIO request state, and private driver state. The comments describe QED as a two-level cluster allocation table: a fixed L1 table points to on-demand L2 tables, which point to data clusters.

Key format constants include default/min/max cluster size, min/max/default table size, `QED_F_BACKING_FILE`, `QED_F_NEED_CHECK`, `QED_F_BACKING_FORMAT_NO_PROBE`, and supported feature masks. `QEDHeader` is packed and stored little-endian on disk. QED table entries use `0` for unallocated clusters and `1` for zero clusters.

`BDRVQEDState` owns the block node, CPU-endian header, `table_lock`, L1 table, L2 cache, table geometry, tracked file size, serialized allocating-write state, and delayed need-check timer. Inline helpers compute cluster starts, cluster offsets, table indexes, table/data offset validity, alignment, and special cluster markers. The header also declares all shared QED routines implemented across `qed.c`, `qed-table.c`, `qed-cluster.c`, `qed-l2-cache.c`, and `qed-check.c`.

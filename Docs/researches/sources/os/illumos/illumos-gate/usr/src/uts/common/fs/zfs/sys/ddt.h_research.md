# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/ddt.h

Read status: complete, 255 lines.

Purpose: deduplication table definitions for on-disk keys/phys records, in-core entries/tables, object operations, stats, repair, and sync.

Key structures and APIs:
- DDT currently declares `DDT_TYPE_ZAP`; classes are ditto, duplicate, and unique.
- `ddt_key_t` stores checksum plus packed logical size, physical size, compression, and encryption state.
- `ddt_phys_t` stores up to `SPA_DVAS_PER_BP` DVAs, refcount, and physical birth TXG.
- `ddt_entry_t` is the in-core dedup entry with all physical variants, lead ZIOs, repair ABD, loading state, condition variable, and AVL linkage.
- `ddt_t` stores per-checksum dedup state, object ids, histograms, cached histograms, object stats, and AVL linkage.
- `ddt_ops_t` abstracts backend object operations: create/destroy/lookup/prefetch/update/remove/walk/count.
- APIs cover object lookup/info/walk, block pointer/key/phys conversion, refcount changes, histogram/stat aggregation, dedup ratio/space queries, ditto-copy decisions, compression, table lookup/prefetch/remove, repair lifecycle, create/load/unload/sync, and backend update.

Important implementation constraints:
- Packed `ddk_prop` uses `BF64_*` macros and is on-disk format sensitive.
- `DDE_GET_NDVAS()` reduces available DVAs when encrypted.
- DDT object type/class search order is encoded in enum ordering.

Dependencies: sysmacros/types, ZFS fs definitions, ZIO, DMU, bitfield helpers, ABD.

Research notes:
- `ddt_zap_ops` is the declared backend.
- DDT ties checksum identity, physical block replicas, dedup stats, and repair workflows together.

# File Research: sources/local-fs/xfsprogs/db/agf.c

Defines the `agf` command and the field layout for allocation group free-space headers. `agf_flds` maps `xfs_agf_t` fields including magic/version, AG sequence/length, bno/cnt/rmap/refcount btree roots and levels, freelist indexes/counts, free block accounting, uuid, lsn, and crc. Root fields have next types such as `TYP_BNOBT`, `TYP_CNTBT`, `TYP_RMAPBT`, and `TYP_REFCBT`, enabling `addr` traversal into btrees.

The `agf` command accepts an optional AG number, validates it against `sb_agcount`, updates `cur_agno`, and sets the cursor to `XFS_AGF_DADDR` for one filesystem sector. `agf_size` reports the sector-sized AGF object in bits. The file integrates with `type.c`/`field.c` through exported field arrays and `agf_init`.

# File Research: sources/os/bsd/netbsd-src/sys/fs/udf/udf_readwrite.c

Read completely: 736 lines.

Implements generic UDF physical-sector I/O, descriptor I/O, descriptor fixups, and strategy dispatch wrappers. It is the common read/write helper layer below UDF metadata code and above the selected disc strategy backend.

Descriptor fixups include `udf_fixup_fid_block()`, which resynchronizes to FID descriptors inside a block, updates each FID tag location, and recalculates tag checksums; `udf_fixup_internal_extattr()`, which fixes embedded extended-attribute header tag locations and CRCs; and `udf_fixup_node_internals()`, which fixes internal FIDs, internal metadata bitmap descriptors, allocation extent CRC length quirks for older UDF versions, and final node descriptor tag/CRC sums.

Physical I/O helpers build top-level buffers and split transfers into nested `MAXPHYS`-sized buffers submitted through `udf_discstrat_queuebuf()`. `udf_read_phys_sectors()` synchronously reads one or more physical sectors. `udf_write_phys_sectors()` and the internal `udf_write_phys_buf()` synchronously write physical sectors while preserving vnode output accounting.

Descriptor readers/writers build on sector I/O. `udf_read_phys_dscr()` reads a descriptor, validates tag and payload checksums, handles empty blocks as “no descriptor”, and expands multi-sector descriptors when `udf_tagsize()` exceeds one sector. `udf_write_phys_dscr_sync()` and `udf_write_phys_dscr_async()` set tag locations, validate tag/CRC sums, and write descriptors either synchronously or with an iodone callback.

The bottom of the file is the strategy vtable facade: create/free/read/write logical-volume descriptors, queue buffers, synchronize caches, initialize a strategy, and finish a strategy by dispatching through `ump->strategy`.

Risk areas include nested buffer lifecycle/accounting, descriptor checksum correctness, and assumptions that logical-space descriptors are at most one sector except where explicitly handled. Some paths panic on unexpected tag types, so corrupted or misclassified buffers must be filtered before these helpers.

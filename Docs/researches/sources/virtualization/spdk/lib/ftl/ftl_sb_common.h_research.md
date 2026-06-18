# File Research: sources/virtualization/spdk/lib/ftl/ftl_sb_common.h

Defines common superblock constants and version-independent packed structures.

Important content:
- `FTL_SUPERBLOCK_SIZE` is 128 KiB.
- `FTL_SUPERBLOCK_MAGIC` is built from four 16-bit constants.
- `ftl_superblock_gc_info` stores high-priority GC band, current band ID, physical reclaim-unit ID, and transaction validity marker.
- `ftl_superblock_header` stores magic, CRC, and version.
- `ftl_superblock_v3_md_region` describes older metadata layout region entries.
- `ftl_superblock_v5_md_blob_hdr` points to variable-size blobs inside the superblock blob area.
- `ftl_superblock_shm` stores shared-memory restart state: SHM ready/clean, in-progress trim info, and GC info.

Static asserts enforce packed structure sizes for disk format stability.

# File Research: sources/virtualization/spdk/lib/ftl/ftl_sb_current.h

Defines the current superblock format, version 5.

`struct ftl_superblock` contains:
- common header and UUID
- current sequence ID
- clean shutdown flag
- surfaced LBA count
- overprovisioning
- maximum relocation queue depth
- upgrade-ready flag
- last L2P checkpoint sequence boundary
- GC info
- blob-area end pointer
- NV-cache and base-device type names
- v5 blob headers for NV-cache metadata layout, base metadata layout, and layout parameters
- flexible blob-area start

Static asserts verify header placement and that the fixed structure fits in `FTL_SUPERBLOCK_SIZE`.

Role: this is the persisted compatibility anchor for FTL startup, shutdown, layout upgrade, and dirty/clean recovery decisions.

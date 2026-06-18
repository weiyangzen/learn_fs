# File Research: sources/virtualization/spdk/lib/ftl/upgrade/ftl_sb_prev.h

Defines previous superblock versions used for upgrade compatibility.

Contents:
- Bug-compatible `FTL_SUPERBLOCK_MAGIC_V2`.
- Version constants v0 through v4.
- Packed/size-checked structs for v2, v3, and v5 superblock layouts.
- v3 includes linked metadata layout head; v5 includes blob-area descriptors for NVC layout, base layout, and layout params.

Role:
- Lets upgrade code reinterpret the current superblock memory as older durable formats.

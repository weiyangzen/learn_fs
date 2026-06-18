# File Research: sources/virtualization/spdk/lib/ftl/upgrade/ftl_sb_upgrade.h

Defines `union ftl_superblock_ver`, a packed overlay for common header, old v2/v3/v5 formats, and current superblock.

Used by superblock version-specific upgrade/load code to reinterpret the same superblock DMA buffer according to header version.

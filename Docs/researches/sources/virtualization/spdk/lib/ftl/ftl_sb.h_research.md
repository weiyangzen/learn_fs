# File Research: sources/virtualization/spdk/lib/ftl/ftl_sb.h

Public header for superblock helpers. It includes common and current superblock definitions and forward-declares `spdk_ftl_dev` and `ftl_layout_region`.

Declared APIs validate magic, inspect/validate/store/load the superblock blob area, upgrade a metadata layout region to a new version, apply the metadata layout from the superblock, and dump the superblock metadata layout.

Architectural role: management and upgrade code use this header to keep version-specific superblock handling behind a small dispatch interface.

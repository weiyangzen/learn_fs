# File Research: sources/virtualization/spdk/lib/ftl/upgrade/ftl_sb_v5.h

Declares v5 superblock APIs for:
- Blob-area empty and validation checks.
- Store/load blob area.
- Upgrade one metadata layout region.
- Apply loaded metadata layout to runtime layout.
- Dump v5 metadata layout.

This is the main interface between current superblock format and layout tracker state.

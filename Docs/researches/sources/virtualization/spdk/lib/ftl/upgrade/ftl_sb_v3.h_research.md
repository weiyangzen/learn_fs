# File Research: sources/virtualization/spdk/lib/ftl/upgrade/ftl_sb_v3.h

Declares v3 superblock helper APIs:
- Magic check.
- Empty layout check.
- Region overflow check.
- Load all metadata regions.
- Dump metadata layout.

Used during old-format load and v4-to-v5 superblock conversion.

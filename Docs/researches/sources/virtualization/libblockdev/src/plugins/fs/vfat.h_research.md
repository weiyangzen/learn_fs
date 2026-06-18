# File Research: sources/virtualization/libblockdev/src/plugins/fs/vfat.h

Declares VFAT info data and operations.

Key contents:
- Defines `BDFSVfatInfo` with `label`, `uuid`, `cluster_size`, `cluster_count`, and `free_cluster_count`.
- Declares copy/free helpers.
- Declares mkfs, check, repair, label, UUID, info, and resize APIs.

Important invariants:
- Size calculations are based on cluster size and cluster counts.
- UUID means FAT volume ID, not a standard UUID.

Filesystem/block relevance:
- Exposes VFAT management operations to generic dispatch.

Notable risks:
- Callers must account for FAT label uppercasing and short label limits.

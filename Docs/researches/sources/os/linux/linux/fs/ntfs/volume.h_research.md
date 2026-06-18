# File Research: sources/os/linux/linux/fs/ntfs/volume.h

Read coverage: complete file, 296 lines.

This header defines the legacy NTFS in-memory volume/superblock structure and inline helpers for volume flags and counters.

Key contents:
- `struct ntfs_volume` stores VFS superblock linkage, mount ownership/mask options, error policy, sector/cluster/MFT/index geometry, volume serial/version/flags/label, upcase and attrdef tables, allocator cursors/zones, system inode references, NLS state, free-space counters, dirty delayed-allocation accounting, a waitqueue, background work item, and preallocation size.
- Defines `NTFS_VOL_UID` and `NTFS_VOL_GID`.
- Enumerates `NV_*` state bits, including errors, visibility toggles, case sensitivity, logfile/quota flags, read-only/shutdown, compression, free-cluster-known, immutability, Windows-name checking, discard, and sparse disabling.
- Macro `DEFINE_NVOL_BIT_OPS()` emits `NVol*`, `NVolSet*`, and `NVolClear*` inline helpers for all flags.
- Inline counter helpers update free clusters, free MFT records, LCN empty-bit page counts, and dirty-cluster reservations.
- Declares `ntfs_available_clusters_count()` and `get_nr_free_clusters()`.

Integration:
- Central state carrier used across legacy NTFS mount, inode, allocation, directory, and metadata code.
- Counter helpers coordinate with `super.c` free-space precomputation via `NVolFreeClusterKnown` and `free_waitq`.

Risks:
- Many fields have cross-file ownership. Cleanup order in `super.c` must match this structure.
- Helpers that wait for `NVolFreeClusterKnown` can block if the background scan never completes.
- Atomic counters track approximations under concurrent allocation and delayed allocation; callers must respect the established locks around bitmap operations.

# File Research: sources/windows/reactos/sdk/lib/fslib/vfatlib/check/fat.h

This header declares FAT table checker operations.

Core contents:
- FAT loading/access/update: `read_fat`, `get_fat`, `set_fat`.
- Cluster classification/navigation: `bad_cluster`, `next_cluster`, `cluster_start`.
- Ownership tracking: `set_owner`, `get_owner`.
- Repair/reclamation: `fix_bad`, `reclaim_free`, `reclaim_file`, `update_free`.

Risk points:
- Functions operate on mutable `DOS_FS` global-style state and generally perform disk writes through `fs_write`.
- Several functions can terminate via `die` on internal inconsistencies.

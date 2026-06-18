# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/tempexch.h

Declares the temporary-file mapping exchange interface used by online repair.

Key elements:
- `struct xrep_tempexch` wraps `struct xfs_exchmaps_req`.
- `xrep_tempexch_trans_reserve` prepares and reserves resources in an existing transaction while both inodes are already locked.
- `xrep_tempexch_trans_alloc` creates a new transaction and locks/joins both inodes for exchange.
- `xrep_tempexch_contents` performs the actual mapping exchange.

Scope:
- Only available under `CONFIG_XFS_ONLINE_REPAIR`.

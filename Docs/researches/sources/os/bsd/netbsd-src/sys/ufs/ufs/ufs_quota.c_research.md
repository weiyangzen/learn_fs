# File Research: sources/os/bsd/netbsd-src/sys/ufs/ufs/ufs_quota.c

This file is the shared quota front end for UFS quota v1 and quota v2. It routes accounting and `quotactl` operations to the active quota implementation and manages the in-core `dquot` cache.

Key responsibilities:
- Initialize/free per-inode quota pointers.
- Dispatch block and inode quota accounting to v1 or v2 implementations.
- Implement generic `quotactl` command handling and authorization.
- Manage the global dquot hash table, pool cache, mutex, and condition variable.
- Create, find, reference, release, sync, and destroy in-core dquot objects.

Important functions:
- `ufsquota_init` / `ufsquota_free`: Initialize or release all quota references attached to an inode.
- `chkdq` / `chkiq`: Skip snapshots, then dispatch block or inode usage updates to `chkdq1`/`chkdq2` and `chkiq1`/`chkiq2`.
- `quota_handle_cmd`: Switches over `QUOTACTL_*` operations and calls typed handlers.
- `quota_handle_cmd_stat`, `idtypestat`, `objtypestat`: Report quota implementation metadata, ID types, and object types.
- `quota_handle_cmd_get` / `put` / `del`: Enforce authorization and delegate quota value lookup, update, and deletion.
- Cursor handlers: Expose quota2 iteration operations through `QUOTACTL_CURSOR*`; v1 generally returns `EOPNOTSUPP`.
- `dqinit`, `dqreinit`, `dqdone`: Manage global quota cache infrastructure.
- `getinoquota`: Attaches user/group dquots to an inode, refreshing them if UID/GID changed.
- `dqget`: Finds or allocates a cached dquot and loads implementation-specific backing state with `dq1get` or `dq2get`.
- `dqref` / `dqrele`: Maintain dquot references and sync modified dquots before final release.
- `qsync`: Dispatches quota sync to v1 or v2.

Important interactions:
- Called from vnode permission, ownership, allocation, and mount paths.
- Uses mount flags `UFS_QUOTA` and `UFS_QUOTA2` to select implementation.
- Coordinates with `ufs_quota1.c`, `ufs_quota2.c`, and `ufsmount.h` quota fields.

Notable behavior and risks:
- `dqget` handles races where another thread allocates the same dquot while the current thread temporarily drops `dqlock`.
- `dqrele` loops while the last referenced dquot is dirty, syncing before removing it from the hash.
- Quota file vnodes are skipped in `getinoquota` to avoid deadlocks from recursively quota-accounting quota files.

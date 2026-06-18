# File Research: sources/os/linux/linux/fs/nfs_common/grace.c

Implements shared lock-manager grace-period tracking for lockd and NFSv4/NFSD state recovery.

Key behavior:
- Maintains a per-network-namespace list of lock managers currently in grace.
- `locks_start_grace()` adds a lock manager to the namespace grace list, warning on double-add attempts.
- `locks_end_grace()` removes a lock manager and is safe to call more than once because the list head is reinitialized.
- `locks_in_grace()` reports whether any lock manager is in grace, meaning ordinary lock requests should be rejected or delayed.
- `opens_in_grace()` reports whether any grace-period participant blocks opens as well as locks.
- Registers per-net operations that initialize and validate the grace list for each network namespace.

Important interactions:
- Exported for lockd and NFSD/NFSv4 state handling.
- Uses a global spinlock plus per-net generic storage to coordinate grace state across lock managers.

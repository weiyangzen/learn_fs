# File Research: sources/os/linux/linux-stable/fs/nfs_common/grace.c

Purpose: Shared infrastructure for NFS/lockd grace periods per network namespace.

Key responsibilities:
- Maintains per-net grace-period lists of `struct lock_manager`.
- `locks_start_grace` adds a lock manager to the namespace grace list.
- `locks_end_grace` removes it, safely allowing repeated end calls.
- `locks_in_grace` reports whether ordinary locks should be blocked.
- `opens_in_grace` reports whether opens should be blocked based on managers with `block_opens`.
- Registers pernet operations to initialize and validate grace lists.

Integration:
- Used by lockd and NFSv4/NFSD state recovery paths.
- `blocklayout.c` checks `locks_in_grace` before issuing pNFS layouts.

Risks and notes:
- Uses a global spinlock for grace list protection.
- Warns on double add and on namespace teardown with non-empty grace list.

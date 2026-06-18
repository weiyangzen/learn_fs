# File Research: sources/os/linux/linux/fs/lockd/procfs.c

Purpose: Provides `/proc/fs/lockd/nlm_end_grace` for reading and ending lockd grace-period state.

Key functionality:
- Write accepts strings beginning with `Y`, `y`, or `1` and calls `locks_end_grace()` for the current network namespace’s `lockd_manager`.
- Read returns `Y\n` when the grace list is empty, otherwise `N\n`.
- Uses `simple_transaction_get()` for write buffering and `simple_transaction_release()` on release.
- `lockd_create_procfs()` creates `fs/lockd` and `nlm_end_grace`.
- `lockd_remove_procfs()` removes both entries.

Dependencies and integration:
- Uses current task net namespace through `current->nsproxy->net_ns`.
- Depends on `lockd_net_id` and `struct lockd_net`.

Risk notes:
- Write parser only inspects the first byte.
- Proc entry is writable by owner/root only and readable by all.
- Namespace selection follows current task namespace at operation time.

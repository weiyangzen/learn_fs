# File Research: sources/os/linux/linux-stable/fs/lockd/procfs.c

Implements procfs control for manually ending lockd grace period.

Interface:
- Creates `/proc/fs/lockd/nlm_end_grace`.
- Read returns `Y\n` when the per-net lock manager grace list is empty, otherwise `N\n`.
- Write accepts strings beginning with `Y`, `y`, or `1`; accepted writes call `locks_end_grace(&ln->lockd_manager)`.
- Uses current task’s network namespace via `current->nsproxy->net_ns`.

Implementation notes:
- Write uses `simple_transaction_get()` and release uses `simple_transaction_release()`.
- `lockd_create_procfs()` creates directory and file, rolling back the directory on failure.
- `lockd_remove_procfs()` removes file and directory.

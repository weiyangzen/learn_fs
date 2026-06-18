# File Research: sources/os/illumos/illumos-gate/usr/src/cmd/zfs/zfs_util.h

Small private utility header for the `zfs` command.

Exports:
- `safe_malloc(size_t size)`: allocation helper that exits on failure.
- `nomem(void)`: fatal out-of-memory handler.
- `g_zfs`: process-global libzfs handle.

Integration role:
- `zfs_main.c` defines all three exported symbols.
- `zfs_iter.c` uses `safe_malloc()`, `nomem()`, and `g_zfs`.
- `zfs_project.c` uses `safe_malloc()`.

Risk notes:
- `g_zfs` makes these helper modules dependent on `zfs_main.c` initialization and unsuitable as independent library code.
- Allocation helpers terminate the process instead of returning errors; callers are written around that fatal behavior.

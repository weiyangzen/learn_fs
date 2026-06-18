# File Research: sources/os/linux/linux-stable/fs/afs/proc.c

## Scope

Implements the `/proc/fs/afs` control and inspection interface for kAFS, including namespace-wide cell/server/stat/sysname files and per-cell volume/VL-server subdirectories.

## APIs And Behavior

- `afs_proc_init()` creates `/proc/fs/afs` entries: `cells`, `rootcell`, `servers`, `stats`, `sysname`, and `addr_prefs`; `afs_proc_cleanup()` removes them.
- `afs_proc_cell_setup()` creates per-cell `vlservers` and `volumes` files; `afs_proc_cell_remove()` removes them.
- `afs_proc_cells_write()` accepts `add <cell> <args>` and preloads/pins cells through `afs_lookup_cell()`.
- `afs_proc_rootcell_write()` initializes the workstation cell once, rejecting paths, relative names, and repeated setup.
- `afs_proc_sysname_write()` replaces the `@sys` substitution list, validating count, path separators, recursion, and dot entries.
- Seq-file show/start/next/stop routines expose cells, address preferences, volumes, VL servers, file servers, sysnames, and aggregate counters.

## State And Dependencies

The file reads and updates `struct afs_net`, `struct afs_cell`, `struct afs_volume`, `struct afs_server`, `struct afs_vlserver`, address preference lists, and `struct afs_sysnames`. Iteration is RCU/read-lock based; sysname replacement uses `sysnames_lock`; root cell setup serializes with the proc inode lock.

## Risks And Invariants

Proc writes are small command parsers and rely on pre-copied kernel buffers from procfs helpers. The sysname list must avoid recursive `@sys` suffixes and path components. VL/server display paths dereference RCU-managed address lists and assume the proc entry's private cell/net data remains valid until removal.

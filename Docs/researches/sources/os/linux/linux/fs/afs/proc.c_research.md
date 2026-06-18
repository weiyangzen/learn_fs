# File Research: sources/os/linux/linux/fs/afs/proc.c

## Purpose
Implements the AFS procfs control and inspection interface for cells, rootcell, address preferences, volume/server status, sysname substitution, and statistics.

## Main Responsibilities
- Creates per-net `/proc/net/afs` entries and per-cell proc subdirectories.
- Displays known cells, VL servers, fileservers, volumes, address preferences, sysnames, and statistics.
- Accepts writes to add cells, set the root cell, configure `@sys` substitutions, and update address preferences.
- Safely iterates RCU-protected cell/server/volume lists and sysname state.

## Key Functions and Data
- `afs_proc_init()` creates `cells`, `rootcell`, `servers`, `stats`, `sysname`, and `addr_prefs`.
- `afs_proc_cell_setup()` creates per-cell `vlservers` and `volumes` files.
- `afs_proc_cells_write()` supports `add <cellname> <addr-list>` and pins manually added cells against GC.
- `afs_proc_rootcell_write()` initializes the workstation cell if it has not already been set.
- `afs_proc_sysname_write()` replaces the `@sys` substitution list with validated tokens.
- `afs_proc_servers_show()` reports fileserver UUIDs, refs/activity, probe state, endpoint list, RTT, errors, and priorities.
- `afs_proc_stats_show()` reports directory and file read/write counters.

## Important Details
- Cell and server listings use RCU sequence helpers; sysname iteration uses `net->sysnames_lock`.
- `sysname` writes reject recursive `@sys` suffixes, slash-containing names, invalid dot names, overlong names, and more than `AFS_NR_SYSNAME` substitutions.
- `rootcell` writes reject dotted names and names containing `/`, and only succeed before a workstation cell already exists.
- DNS source/status strings are normalized for VL server display.

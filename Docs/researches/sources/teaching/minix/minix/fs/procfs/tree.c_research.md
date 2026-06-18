# File Research: sources/teaching/minix/minix/fs/procfs/tree.c

`tree.c` manages ProcFS's dynamic PID directories and implements the VTreeFS hooks registered by `main.c`. It maintains `proc_list[NR_PROCS]`, computes the number of per-PID files from `pid_files`, and updates process state through `__sysctl(CTL_MINIX, MINIX_PROC, PROC_LIST)`.

`pid_from_slot` maps kernel task slots to negative task PIDs and process slots to active process IDs. `make_stat` builds inode metadata for PID directories and their files, assigning root ownership for tasks and process uid/gid for user processes. `check_owner` forces directory reconstruction when process ownership changes.

`construct_pid_dirs` refreshes root-level PID directories in two passes: delete stale/mismatched entries first, then add missing current entries. This avoids VTreeFS assertions and duplicate names during rapid PID reuse. `construct_pid_entries` adds one requested PID file or all PID files, deleting the parent if the process has disappeared.

`lookup_hook` lazily refreshes process data once per tick, then rebuilds root PID directories, creates requested PID entries, or delegates service-directory lookup refresh. `getdents_hook` eagerly prepares directory contents for root, PID directories, or service. `read_hook` initializes the output buffer and dispatches to PID-file, service-file, or static-root generator callbacks based on inode indexes. `rdlink_hook` has placeholder support for PID-directory symlinks through `pid_link`, which currently returns an empty target.

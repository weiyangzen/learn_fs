# File Research: sources/os/bsd/dragonflybsd/sys/vfs/procfs/procfs_subr.c

This file implements procfs vnode allocation, caching, process lookup helpers, generic read/write dispatch, user-string parsing, name-map lookup, and process-exit cleanup.

`procfs_allocvp()` hashes pfsnodes by pid, reuses existing vnode/pfsnode pairs for the same mount/pid/type, and allocates new vnodes with synthetic type/mode based on `pfstype`. `procfs_freevp()` removes a pfsnode from the hash and frees it.

`pfs_pfind()` and `pfs_zpfind()` return referenced processes with `p_token` held and reject processes in post-exit state. `pfs_pdone()` releases the token and process reference.

`procfs_rw()` routes reads/writes for note, regs, fpregs, dbregs, ctl, status, map, mem, type, cmdline, and rlimit. It obtains the current process from the uio thread, finds the target process, holds its first LWP, locks the pfsnode, calls the per-file handler, and posts kqueue write notes on successful writes.

`procfs_exit()` marks matching pfsnodes with `PFS_DEAD` and recycles their vnodes when a process exits, avoiding unsafe direct `vgone()` of active descriptors.

Research notes: pfsnode caching is mount-aware, because procfs can be mounted more than once. Exit handling is deliberately careful around active vnode references.

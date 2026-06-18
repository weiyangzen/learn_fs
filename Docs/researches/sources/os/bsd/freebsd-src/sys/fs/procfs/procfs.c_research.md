# File Research: sources/os/bsd/freebsd-src/sys/fs/procfs/procfs.c

## Purpose

Defines the FreeBSD `procfs` pseudofs instance and registers the process-oriented file hierarchy under `/proc`. It supplies shared attribute and visibility callbacks plus simple filler callbacks for `curproc`, `self`, and executable path links.

## Main Entry Points

`procfs_init()` builds the tree:
- root links: `curproc`, `self`.
- process directory: `pid`, marked `PFS_PROCDEP`.
- per-process files: `cmdline`, `dbregs`, `etype`, `fpregs`, `map`, `mem`, `note`, `notepg`, `regs`, `rlimit`, `status`, `osrel`.
- per-process links: `file`, `exe`.

`procfs_doprocfile()` returns the process binary path using `proc_get_binpath()`.

`procfs_docurproc()` emits the current process pid.

`procfs_attr_all_rx()`, `procfs_attr_rw()`, and `procfs_attr_w()` wrap `procfs_attr()` to set fixed file modes. For setuid/setgid-exec processes, non-process-directory entries are hidden by setting mode `0`.

`procfs_notsystem()` hides entries for `P_SYSTEM` processes.

`procfs_candebug()` exposes entries only for non-system processes that pass `p_candebug()`.

`procfs_uninit()` has no explicit cleanup because pseudofs garbage-collects the constructed tree.

## Integration Points

The file uses the `PSEUDOFS(procfs, 1, VFCF_JAIL)` macro from pseudofs to register VFS operations and module dependency. Most content handlers are implemented in the sibling `procfs_*.c` files and declared by `procfs.h`.

## Risks and Review Notes

Visibility and permission behavior relies on callers honoring pseudofs callback locking rules: attribute and visibility callbacks expect the target process lock held. Debug-sensitive nodes use both `procfs_candebug()` at lookup/visibility time and deeper checks in their file handlers.

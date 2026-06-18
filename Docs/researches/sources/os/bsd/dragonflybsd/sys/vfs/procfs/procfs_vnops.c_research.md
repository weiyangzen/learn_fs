# File Research: sources/os/bsd/dragonflybsd/sys/vfs/procfs/procfs_vnops.c

This file implements procfs vnode operations and directory topology. `procfs_vnode_vops` routes reads/writes to `procfs_rw`, lookup/readdir/readlink/getattr/open/close/ioctl/kqfilter to local handlers, and rejects creation/removal/rename-type operations with bad ops or read-only errors.

The `proc_targets` table defines process-directory entries: `.`, `..`, `mem`, `regs`, `fpregs`, `dbregs`, `ctl`, `status`, `note`, `notepg`, `map`, `etype`, `cmdline`, `rlimit`, `file`, and `exe`, with validity predicates for register/map/type files.

`procfs_lookup()` resolves root entries (`curproc`, `self`, numeric pids) and process-directory entries, applying jail visibility and `ps_showallprocs` filtering. It returns read-only errors for delete/rename/create attempts.

`procfs_readdir_root()` emits `.`, `..`, `curproc`, `self`, then visible process directories via `allproc_scan()`. `procfs_readdir_proc()` emits visible per-process target entries. `procfs_readlink()` resolves `curproc` to the current pid and `file`/`exe` to the executable path or `unknown`.

`procfs_open()` enforces exclusive write semantics and debug authorization for `Pmem`. `procfs_close()` clears exclusive flags and may clear process stop/step state on final close unless `PF_LINGER` is set. `procfs_ioctl()` implements procfs debugging ioctls for stop-event masks, flags, status, wait, and continue.

`procfs_getattr()` synthesizes attributes, masks debug-sensitive file permissions for setuid/setgid processes, sets register file sizes from register struct sizes, and reports symlink sizes for `curproc` and executable path links. Kqueue filters support read/write/vnode notifications and revoke handling.

Research notes: this is the main policy surface for procfs visibility and debugging control. Security checks are distributed across lookup/open/ioctl/read-write handlers, so changes must preserve jail, uid, setuid, and process-state restrictions.

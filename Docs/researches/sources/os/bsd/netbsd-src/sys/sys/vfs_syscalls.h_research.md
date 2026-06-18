# File Research: sources/os/bsd/netbsd-src/sys/sys/vfs_syscalls.h

Read completely: 93 lines.

Declares shared VFS syscall helper routines, mainly for compat and syscall implementations.

Key elements:
- Forward-declares `stat`, `statvfs`, and `quotactl_args`.
- Declares helpers for stat/statat/file-handle stat, statvfs/fstatvfs/getvfsstat, and file-handle open.
- Declares timestamp update helpers for `utimes`, `utimens`, and `utimensat`.
- Declares `do_open`, file-handle copyin/free helpers, link/unlink/rename/mknod/chmod/chown/access/mkdir/symlink/quotactl/sync/chdir/fchdir helpers, and `vfs_syncwait()`.
- Declares `chdir_lookup()`, `change_root()`, and mount compatibility name table.

Risks and notes:
- These helpers sit on syscall/VFS boundaries and use `enum uio_seg` to distinguish user vs kernel buffers.
- Compat code depends on stable helper semantics for older syscall ABIs.

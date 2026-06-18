# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/syscall.h

`syscall.h` defines illumos system call numbers for use with `syscall(SYS_xxx, ...)` and kernel/user syscall tables. The enumeration begins at 1, while `SYS_syscall` remains 0 as the indirect syscall mechanism on SunOS/SPARC.

The file assigns syscall numbers for classic process, file, filesystem, IPC, signal, VM, scheduling, LWP, large-file, zones, socket, port, timer, door, privilege, audit, processor, and administrative interfaces. Many multiplexed syscalls include comments documenting subcodes, including `pgrpsys`, `msgsys`, `shmsys`, `semsys`, `utssys`, `tasksys`, `exacctsys`, `getpagesizes`, `rctlsys`, `sidsys`, `lwp_park`, `sendfilev`, `privsys`, `ucredsys`, `sigpending`, `context`, `utimesys`, `forksys`, `kaio`, `lgrpsys`/`meminfosys`, `rusagesys`, `port`, `lwp_rwlock_sys`, `zone`, and door operations.

Filesystem-relevant entries include open/close/read/write, link/unlink/symlink/readlink variants, stat/fstat/lstat and 64-bit variants, mount/umount2, sync/fdsync, chdir/fchdir/chroot/fchroot, rename/renameat, mkdir/rmdir/mknod and `*at` variants, statvfs/fstatvfs and 64-bit variants, pathconf/fpathconf, getdents/getdents64, mmap/mmap64/mmapobj, mincore, memcntl, sendfilev, sharefs, autofssys, and ACL/facl.

The tail defines `sysset_t` as 16 32-bit words for syscall sets and `sysret_t` with two long return values. User-level declarations expose `syscall()`, `__systemcall()` returning `sysret_t`, and `__set_errno()` when not compiling the kernel.

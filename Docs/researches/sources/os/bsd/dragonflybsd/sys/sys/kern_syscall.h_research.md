# File Research: sources/os/bsd/dragonflybsd/sys/sys/kern_syscall.h

Kernel-only header collecting internal syscall helper prototypes. It groups descriptors, exec, wait, signals, generic I/O, limits, sockets, pipes, VFS syscalls, time, cwd, and mmap helpers.

Filesystem-relevant helpers include `kern_access`, `kern_chdir`, `kern_chmod`, `kern_chown`, `kern_chroot`, `kern_fstatfs`, `kern_fstatvfs`, `kern_ftruncate`, `kern_getdirentries`, `kern_link`, `kern_mountctl`, `kern_mkdir`, `kern_mknod`, `kern_open`, `kern_readlink`, `kern_rename`, `kern_stat`, `kern_statfs`, `kern_statvfs`, `kern_symlink`, `kern_truncate`, `kern_unlink`, `kern_fsync`, and `kern_mmap`. These are the reusable kernel-side entry points behind system call wrappers.

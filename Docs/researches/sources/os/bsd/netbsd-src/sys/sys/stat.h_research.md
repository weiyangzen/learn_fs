# File Research: sources/os/bsd/netbsd-src/sys/sys/stat.h

Read completely: 299 lines.

This public filesystem metadata header defines `struct stat`, file mode bits, type-test macros, file flags, special timestamp constants, and file-status/manipulation prototypes. `struct stat` includes device, mode, inode, link count, uid/gid, rdev, access/modify/change/birth times, size, block count/size, flags, generation, and spare fields.

It conditionally exposes timespec fields for POSIX.1-2008/XPG7/NetBSD modes and compatibility second/nanosecond fields otherwise. It defines permission masks, file-type constants, `S_IS*` tests, NetBSD access/default permission masks, user/superuser file flags, kernel shorthand flags, `UTIME_NOW`, and `UTIME_OMIT`.

Userland prototypes include chmod/mkdir/mkfifo/stat/fstat/lstat/fchmod/mknod, NetBSD chflags/lchmod variants, and `*at`/utimens APIs under modern feature modes.

Risks: `struct stat` is a core ABI with versioned syscall names. Feature-test macros change visible field names and prototypes, so compatibility code must include the correct mode.

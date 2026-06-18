# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fcntl.h

## Role

`fcntl.h` defines illumos file open flags, `fcntl()` command numbers, file-lock structures, lock/share constants, openat-style flags, and file-advice constants. It is a core filesystem and file-descriptor ABI header.

## Open Flags And Fcntl Commands

- Access modes include `O_RDONLY`, `O_WRONLY`, `O_RDWR`, `O_SEARCH`, and `O_EXEC`.
- Defines common open flags such as `O_NDELAY`, `O_APPEND`, `O_SYNC`, `O_DSYNC`, `O_RSYNC`, `O_NONBLOCK`, `O_LARGEFILE`, `O_CREAT`, `O_TRUNC`, `O_EXCL`, `O_NOCTTY`, `O_XATTR`, `O_NOFOLLOW`, `O_NOLINKS`, `O_CLOEXEC`, `O_DIRECTORY`, `O_DIRECT`, and `O_CLOFORK`, gated by feature-test macros where required.
- Defines descriptor/file commands: duplicate/get/set FD flags, get/set file flags, get extended flags, stream/private/quota/blocksize commands, socket owner commands, revoke, remote-lock query, share/unshare, poison FD, and close-on-exec/close-on-fork duplicate variants including `F_DUP3FD`.
- Kernel/KMEMUSER exposes old SVR3 `F_O_GETLK` and sysid/node-id extraction macros for clustering/remote locks.

## Locking ABI

- Defines command numbers for native and ILP32 large-file lock/space commands. Values differ based on `_LP64`, `_FILE_OFFSET_BITS`, and `_LARGEFILE64_SOURCE`.
- Supports classic POSIX locks, NBMAND private variants, open-file-description locks, and private flock-owned locks.
- Defines `flock_t`, 32-bit `flock32_t`, large-file `flock64_t`, 32-bit packed `flock64_32_t`, LP64 kernel view `flock64_64_t`, and old SVR3 `o_flock_t`.
- Lock types are `F_RDLCK`, `F_WRLCK`, `F_UNLCK`, and `F_UNLKSYS`.

## Share, At, And Advice Constants

- Defines `O_ACCMODE`, `FD_CLOEXEC`, and `FD_CLOFORK`.
- Defines direct I/O toggles `DIRECTIO_OFF` and `DIRECTIO_ON`.
- Defines `fshare_t` and share access/deny masks including private delete/metadata/mandatory enforcement flags.
- Defines `AT_FDCWD`, symlink follow/no-follow flags, `AT_REMOVEDIR`, `_AT_TRIGGER`, and `AT_EACCESS`.
- Defines `POSIX_FADV_*` constants for `posix_fadvise()`.

## Filesystem Relevance

This header is central to VFS/open/lock/share behavior. The conditional command numbering and structure packing are especially important for 32-bit, large-file, and kernel compatibility paths.

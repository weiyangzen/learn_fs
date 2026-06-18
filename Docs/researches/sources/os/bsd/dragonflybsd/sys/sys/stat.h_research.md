# File Research: sources/os/bsd/dragonflybsd/sys/sys/stat.h

This header defines file status ABI: `struct stat`, file mode/type bits, file flag bits, timestamp macros, POSIX stat-related constants, and userland filesystem metadata function declarations.

Key responsibilities:
- Defines filesystem-related types if needed:
  - `blkcnt_t`, `blksize_t`, `dev_t`, `gid_t`, `ino_t`, `mode_t`, `nlink_t`, `off_t`, `time_t`, `uid_t`
- Defines `struct stat`:
  - inode, link count, device, mode, owner/group, rdev
  - access/modify/change `timespec`
  - size, blocks, legacy blocksize field
  - flags, generation, spare fields
  - current `st_blksize`
- Defines time aliases:
  - `st_atime`, `st_mtime`, `st_ctime`
  - BSD `st_atimespec`, `st_mtimespec`, `st_ctimespec`
- Defines permission bits and aliases:
  - setuid/setgid/sticky
  - owner/group/other rwx masks
  - BSD read/write/exec aliases
- Defines file type bits and test macros:
  - fifo, char, dir, block, regular, symlink, socket
  - BSD DB and whiteout
- Defines POSIX `S_TYPEISMQ`, `S_TYPEISSEM`, and `S_TYPEISSHM` as zero.
- Defines BSD mode constants:
  - `ACCESSPERMS`
  - `ALLPERMS`
  - `DEFFILEMODE`
  - `S_BLKSIZE`
- Defines user and superuser file flags:
  - `UF_NODUMP`, immutable, append, opaque, nounlink, nohistory, cache, xlink
  - `SF_ARCHIVED`, immutable, append, nounlink, nohistory, nocache, xlink
- Defines kernel shorthand flags:
  - `OPAQUE`
  - `APPEND`
  - `IMMUTABLE`
  - `NOUNLINK`
- Defines POSIX.1-2008 timestamp constants `UTIME_NOW` and `UTIME_OMIT`.
- Declares userland APIs:
  - chmod/fchmod/fchmodat
  - futimens/utimensat
  - fstat/lstat/stat/fstatat
  - mkdir/mkdirat
  - mkfifo/mkfifoat
  - mknod/mknodat
  - umask
  - BSD chflags/fchflags/lchflags/chflagsat/lchmod

Important invariants:
- `struct stat` preserves `__old_st_blksize` for old ABI compatibility while using `st_blksize` later.
- File mode constants must remain consistent with `<fcntl.h>`.
- POSIX IPC object type test macros return zero because these are not implemented as distinct file types.
- `UF_SETTABLE` and `SF_SETTABLE` partition owner-changeable and superuser-changeable flag spaces.

Research notes:
- This is a stable filesystem metadata ABI header and directly relevant to VFS/stat syscall compatibility.

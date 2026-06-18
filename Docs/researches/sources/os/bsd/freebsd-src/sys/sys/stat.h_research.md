# File Research: sources/os/bsd/freebsd-src/sys/sys/stat.h

## Purpose
`stat.h` defines the FreeBSD file status ABI, file mode/type macros, file flags, timestamp aliases, and userland stat/chmod/mkdir-style function prototypes.

## Main Interfaces
- Declares standard typedefs including `blksize_t`, `blkcnt_t`, `dev_t`, `fflags_t`, `gid_t`, `ino_t`, `mode_t`, `nlink_t`, `off_t`, and `uid_t`.
- Defines current `struct stat` with device, inode, link count, mode, BSD flags, owner IDs, rdev, access/modify/change/birth times, size, blocks, block size, file flags, generation, revision, and spare fields.
- Kernel compatibility structs include `ostat`, `freebsd11_stat`, and `nstat`.
- Defines permission bits, file type bits, `S_IS*()` tests, BSD file flags (`UF_*`, `SF_*`), and timestamp compatibility aliases.
- Declares userland APIs including `stat`, `fstat`, `lstat`, `fstatat`, `chmod`, `fchmodat`, `mkdir`, `mkfifo`, `mknod`, `utimensat`, and flags variants.

## Implementation Notes
The i386 ABI has extra time extension fields. Compatibility structs preserve old layout for legacy syscalls. BSD-visible sections expose file flags, whiteout type checks, and compatibility names such as `st_birthtime`.

## Dependencies and Constraints
Includes `sys/cdefs.h`, `sys/_timespec.h`, and `sys/_types.h`. Non-kernel BSD-visible builds include `sys/time.h`, with a comment noting namespace pollution.

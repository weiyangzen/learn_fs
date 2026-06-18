# File Research: sources/os/bsd/freebsd-src/sys/sys/fcntl.h

## Purpose
Defines open, fcntl, advisory locking, `*at`, file sealing, and space-control flags plus userland prototypes.

## Main Interfaces
- Typedef guards for `mode_t`, `off_t`, `pid_t`.
- Open/status flags: `O_RDONLY`, `O_WRONLY`, `O_RDWR`, `O_NONBLOCK`, `O_APPEND`, `O_SYNC`, `O_CREAT`, `O_TRUNC`, `O_EXCL`, `O_NOCTTY`, `O_DIRECT`, `O_DIRECTORY`, `O_EXEC`, `O_CLOEXEC`, `O_VERIFY`, `O_PATH`, `O_RESOLVE_BENEATH`, `O_DSYNC`, `O_EMPTY_PATH`, `O_NAMEDATTR`, `O_CLOFORK`.
- Kernel conversion helpers: `FFLAGS`, `OFLAGS`, `FMASK`, `FCNTLFLAGS`, `FUSERALLOWED`.
- `*at` constants: `AT_FDCWD`, `AT_EACCESS`, `AT_SYMLINK_*`, `AT_REMOVEDIR`, `AT_RESOLVE_BENEATH`, `AT_EMPTY_PATH`, rename flags.
- `fcntl` commands: `F_DUPFD`, `F_GETFD`, `F_SETFD`, `F_GETFL`, `F_SETFL`, lock commands, duplicate-with-flags commands, seals, `F_KINFO`, `F_DUP3FD`, `F_DUPFD_CLOFORK`.
- FD flags: `FD_CLOEXEC`, `FD_RESOLVE_BENEATH`, `FD_CLOFORK`.
- Locking: `struct flock`, `struct __oflock`, `LOCK_*`, kernel lock-mode flags.
- Space control: `struct spacectl_range`, `SPACECTL_DEALLOC`.
- Advice constants for `posix_fadvise`.
- Userland prototypes: `open`, `creat`, `fcntl`, `flock`, `fspacectl`, `openat`, `posix_fadvise`, `posix_fallocate`.

## Dependencies And Integration
Shared by libc and kernel. Kernel file flags are a superset of open/fcntl flags, with careful conversion between `O_*` and `F*` encodings.

## Risk Notes
Flag bits are scarce and ABI-sensitive. The header explicitly warns that new `O_*` bits must be coordinated. `FFLAGS/OFLAGS` behavior around `O_EXEC` and `O_PATH` is important for descriptor permission semantics.

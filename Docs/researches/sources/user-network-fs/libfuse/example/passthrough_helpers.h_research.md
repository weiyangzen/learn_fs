# sources/user-network-fs/libfuse/example/passthrough_helpers.h

## Purpose
`passthrough_helpers.h` provides small portability helpers shared by passthrough examples. It abstracts fallocate support across Linux/POSIX/FreeBSD-style APIs and centralizes creation of backing filesystem nodes for FUSE mknod-like operations.

## Important APIs, Types, and Functions
`do_fallocate(int fd, int mode, off_t offset, off_t length)` maps to `fallocate`, `posix_fallocate` for mode zero, or FreeBSD `fspacectl` for punch-hole keep-size mode `0x3`, returning negative errno-style errors. `mknod_wrapper(int dirfd, const char *path, const char *link, int mode, dev_t rdev)` chooses `openat`, `mkdirat`, `symlinkat`, `mkfifoat`, FreeBSD socket creation via `bindat`, or `mknodat`.

## Control Flow
Callers use `do_fallocate()` from FUSE fallocate handlers and pass its return value directly or after sign conversion depending on API style. Callers use `mknod_wrapper()` for regular files, directories, symlinks, FIFOs, sockets on FreeBSD, and device nodes. The helper relies on mode type bits to choose the syscall.

## State and Persistence
The header keeps no state. It changes persistent backing filesystem state by creating files/nodes or allocating/deallocating space. Errors are communicated via return values and `errno` depending on helper.

## Dependencies and Integration Points
It depends on compile-time feature macros `HAVE_FALLOCATE`, `HAVE_POSIX_FALLOCATE`, and `HAVE_FSPACECTL`, plus FreeBSD socket headers for socket-file creation. It is integrated by `passthrough.c`, `passthrough_fh.c`, `passthrough_ll.c`, and `passthrough_hp.cc`.

## Risks
Return-value conventions differ: `do_fallocate()` returns negative errno values, while `mknod_wrapper()` returns syscall-style `-1` with `errno`. Callers must not mix those conventions. The FreeBSD socket path checks `strlen(path)` against `sun_path`, but uses the relative path with `bindat`; portability depends on that platform API. `posix_fallocate` is used only for mode zero, so other modes return `EOPNOTSUPP`.

## Test Signals
Build passthrough examples under different feature macro configurations. Test regular file, directory, symlink, FIFO, and device creation where permitted. Test fallocate mode zero, unsupported modes, and punch-hole mode on FreeBSD with `HAVE_FSPACECTL`.

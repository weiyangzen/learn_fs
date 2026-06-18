# File Research: sources/os/bsd/openbsd-src/sys/kern/kern_descrip.c

## Purpose
Implements process file descriptor tables, file object allocation/lifetime, descriptor duplication, close, fcntl, flock, fd-table fork/exec behavior, and `/dev/fd` duplication support.

## Main Responsibilities
- Initializes file and filedesc pools in `filedesc_init()`.
- Maintains descriptor allocation bitmaps with `fd_used()`, `fd_unused()`, `find_next_zero()`, and `find_last_set()`.
- Provides safe file reference lookup with `fd_getfile()` and `fd_getfile_mode()`.
- Implements `dup`, `dup2`, `dup3`, and `fcntl(F_DUPFD*)` via `dodup3()` and `finishdup()`.
- Implements `fcntl()` flags, async ownership, POSIX advisory locks, and lock queries.
- Implements `close`, `fstat`, `fpathconf`, `flock`, `closefrom`, and `getdtablecount`.
- Allocates and expands fd tables through `fdalloc()` and `fdexpand()`.
- Creates file objects with `falloc()` / `fnew()` and destroys them with `closef()` / `fdrop()`.
- Shares, copies, and frees file descriptor tables for fork/exit with `fdshare()`, `fdcopy()`, and `fdfree()`.
- Handles close-on-exec and close-on-fork in `fdprepforexec()`.

## Key Data
- Global `filehead`, `numfiles`, `file_pool`, `fdesc_pool`.
- `fhdlk`: protects global file list and must work with and without `KERNEL_LOCK()`.
- `fd_fplock`: synchronizes descriptor slots with `fd_getfile()`.
- `fd_lomap` / `fd_himap`: two-level bitmap for free descriptor search.
- `UF_EXCLOSE`, `UF_FORKCLOSE`, `UF_PLEDGEOPEN`, `UF_PLEDGED`: per-fd flags.

## Notable Behavior
- `finishdup()` installs the new file pointer under `fd_fplock`, copies/adjusts fd flags, closes replaced descriptors after dropping the fd table lock, and notifies kqueue via `knote_fdclose()`.
- `fdcopy()` skips close-on-fork descriptors, kqueue descriptors, and descriptors whose reference count is too high.
- `closef()` handles POSIX record lock cleanup before dropping the final file reference.
- `dupfdopen()` supports `/dev/fd/N`, with additional checks for sugid execution.

## Dependencies
Interacts heavily with VFS/vnodes, kqueue close notifications, pledge, ktrace, resource limits, sockets/pipes, credentials, and advisory locking.

## Research Notes
The file carefully separates descriptor-table locking from file-reference locking so concurrent close/dup and lookup can be made race-resistant.

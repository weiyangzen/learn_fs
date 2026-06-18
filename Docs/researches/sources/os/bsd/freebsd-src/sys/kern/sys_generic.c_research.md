# File Research: sources/os/bsd/freebsd-src/sys/kern/sys_generic.c

## Purpose

Implements many generic FreeBSD file-descriptor syscalls and helpers: read/write families, truncate, ioctl, space allocation/deallocation, special file descriptor creation, select/pselect, poll/ppoll, selinfo wakeups, `kcmp`, and extended-error reporting.

## Main responsibilities

- Generic read paths:
  - `sys_read()`, `sys_pread()`, `sys_readv()`, `sys_preadv()`
  - `kern_readv()`, `kern_pread()`, `kern_preadv()`
  - `dofileread()`
- Generic write paths:
  - `sys_write()`, `sys_pwrite()`, `sys_writev()`, `sys_pwritev()`
  - `kern_writev()`, `kern_pwrite()`, `kern_pwritev()`
  - `dofilewrite()`
- File sizing and allocation:
  - `kern_ftruncate()`
  - `kern_posix_fallocate()`
  - `kern_fspacectl()`
- Ioctl:
  - `sys_ioctl()`
  - `kern_ioctl()`
- Special descriptors:
  - `kern_specialfd()`
  - `sys___specialfd()`
- Event wait APIs:
  - `kern_select()`, `sys_select()`, `sys_pselect()`
  - `kern_poll()`, `kern_poll_kfds()`, `sys_poll()`, `sys_ppoll()`
  - select/poll registration and wakeup helpers.
- Utility:
  - `kern_posix_error()`
  - `kern_kcmp()`, `file_kcmp_generic()`
  - extended error setup/copyout/debug printing.

## Key data structures

- `struct seltd`
  - Per-thread select/poll tracking, condition variable, pending/rescan flags, and reusable `selfd` slots.
- `struct selfd`
  - A registration linking one thread wait to one `selinfo`.
- `M_IOCTLOPS`, `M_SELECT`, `M_IOV`, `M_SELFD`
  - Allocation types for ioctl buffers, select buffers, iovecs, and select fd registrations.

## Important read/write behavior

- Single-buffer syscalls construct a one-element `uio`; vector syscalls use `copyinuio()`.
- `fget_read()`/`fget_write()` enforce fd validity and Capsicum rights.
- Positioned I/O requires `DFLAG_SEEKABLE`, except negative offsets are allowed only for character vnodes.
- `dofileread()` and `dofilewrite()` set `uio_rw`, `uio_offset`, and `uio_td`, call fileops, handle short transfers interrupted by restartable errors, emit ktrace records, and set `td_retval[0]`.
- `dofilewrite()` sends `SIGPIPE` on `EPIPE` for non-socket file types.

## Ioctl behavior

- `sys_ioctl()` validates the encoded ioctl direction/size, uses a stack buffer for small payloads, copies data in/out, and delegates to `kern_ioctl()`.
- `kern_ioctl()` handles descriptor close-on-exec operations directly, enforces Capsicum ioctl command rights, holds the file, validates read/write mode, handles `FIONBIO`/`FIOASYNC` file flag synchronization, and otherwise calls `fo_ioctl()`.

## Space-management behavior

- `kern_ftruncate()` requires nonnegative length and writable descriptor.
- `kern_posix_fallocate()` checks offset/length/wrap, requires seekable writable file, and calls `fo_fallocate()`.
- `kern_fspacectl()` currently supports `SPACECTL_DEALLOC`, validates ranges/flags, requires seekable writable file, calls `fo_fspacectl()`, and suppresses restart errors after partial progress.

## Select/poll behavior

- `kern_select()` copies input fd sets, handles ABI fd-bit width and endian conversion, validates high bits beyond open fds, computes timeout, initializes per-thread select state, scans descriptors, sleeps, rescans pending selfd registrations, clears registrations, and copies output fd sets.
- `selscan()` registers interest through `selrecord()` after preallocating selfd entries.
- `selrescan()` rechecks only descriptors whose `selinfo` woke the thread.
- `kern_poll()` copies user pollfd arrays into stack or heap buffers, delegates to `kern_poll_kfds()`, then copies `revents` out.
- `pollscan()` and `pollrescan()` mirror the select logic for pollfd arrays.
- `doselwakeup()` removes waiters from a `selinfo`, marks their `seltd` pending, wakes condition variables, and clears `sf_si` with release semantics.
- `seldrain()` uses wakeup logic to drain waiters during object teardown.

## Special descriptor integration

- `kern_specialfd()` creates eventfd and inotify descriptors through type-specific helpers, then installs the file descriptor.
- `sys___specialfd()` validates ABI struct sizes and flags before delegating.
- This file directly connects `sys_eventfd.c` into the generic syscall surface.

## Extended errors and comparison

- `kern_kcmp()` compares file objects, file tables, signal handlers, or vmspaces between processes after permission checks.
- `exterr_set()`, `exterr_copyout()`, and `sys_exterrctl()` manage optional user-visible extended errno metadata.
- `kern_posix_error()` converts internal errno returns to POSIX-style positive return values for `posix_*` syscalls.

## Filesystem/storage relevance

This is a central VFS syscall front end. It does not implement specific filesystems, but it routes read/write/truncate/ioctl/fallocate/deallocate/select/poll requests into file operations (`fo_read`, `fo_write`, `fo_truncate`, `fo_ioctl`, `fo_fallocate`, `fo_fspacectl`, `fo_poll`). Filesystem behavior appears behind these fileops, so this file defines syscall-level validation, capability checks, offset semantics, signal behavior, ktrace/audit hooks, and readiness waiting semantics.

## Edge cases and safeguards

- I/O sizes are capped by `IOSIZE_MAX`; LP64 has sysctls to clamp to `INT_MAX`.
- `select_check_badfd()` preserves historical `EBADF` behavior for bits set beyond open descriptors.
- Poll array length is bounded by `kern_poll_maxfds()`.
- `select`/`poll` convert `ERESTART` to `EINTR` and `EWOULDBLOCK` to success timeout.
- Selection registration uses preallocated `selfd` entries to avoid allocation after fileops have begun polling.
- Wakeup/free races are handled with selinfo locking and atomic load/store ordering around `sf_si`.

## Research notes

Classify this as generic fd syscall and event-wait infrastructure. It is one of the highest-value syscall boundary files for filesystem behavior because it defines how user I/O requests become VFS/fileops calls.

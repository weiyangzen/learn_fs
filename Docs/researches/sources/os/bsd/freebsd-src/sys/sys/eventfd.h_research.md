# File Research: sources/os/bsd/freebsd-src/sys/sys/eventfd.h

## Purpose
Declares FreeBSD eventfd-compatible counter file descriptor API and kernel hooks.

## Main Interfaces
- `eventfd_t` as `uint64_t`.
- Flags: `EFD_SEMAPHORE`, `EFD_NONBLOCK`, `EFD_CLOEXEC`.
- Kernel APIs:
  - `eventfd_create_file`
  - `eventfd_get`
  - `eventfd_put`
  - `eventfd_signal`
- Userland APIs:
  - `eventfd`
  - `eventfd_read`
  - `eventfd_write`

## Dependencies And Integration
Includes `sys/types.h`. Kernel APIs integrate with `struct file` and `struct thread` without exposing the internal `struct eventfd`.

## Risk Notes
Flag values match file descriptor and nonblocking conventions. `eventfd_get`/`put` imply reference management that callers must pair correctly.

# File Research: sources/os/bsd/freebsd-src/sys/sys/errno.h

## Purpose
Defines FreeBSD errno values for userland and kernel code, including POSIX errors, BSD extensions, capability-mode errors, and kernel-only pseudo-errors.

## Main Interfaces
- Userland `errno` macro maps to `(*__error())`.
- Standard errors `EPERM` through `EINTEGRITY`, with `ELAST` equal to `97`.
- POSIX namespace gates hide non-POSIX names under `_POSIX_SOURCE`.
- Kernel/standalone pseudo-errors:
  - `ERESTART`
  - `EJUSTRETURN`
  - `ENOIOCTL`
  - `EDIRIOCTL`
  - `ERELOOKUP`
- Optional C11 bounds-checking typedef `errno_t` when extension visibility allows it.

## Dependencies And Integration
Userland includes `sys/cdefs.h` for declarations. Kernel code uses the same numeric errno definitions and additionally relies on negative pseudo-errors for syscall and ioctl control flow.

## Risk Notes
Errno numbers are ABI. New errors must not disturb existing values or `ELAST`. Pseudo-errors are internal control signals and should not leak as user-visible errno values.

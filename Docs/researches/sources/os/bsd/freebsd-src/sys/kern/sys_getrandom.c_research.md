# File Research: sources/os/bsd/freebsd-src/sys/kern/sys_getrandom.c

## Purpose

Implements the `getrandom(2)` syscall wrapper over FreeBSD `random(4)` output using a `uio` and Linux-compatible flag handling.

## Main responsibilities

- Validate `getrandom` flags and buffer length.
- Translate `GRND_INSECURE` into nonblocking behavior.
- Build a user-space read `uio`.
- Call `read_random_uio()`.
- Return the number of bytes copied in `td_retval[0]`.

## Important behavior

- Valid flags are `GRND_NONBLOCK`, `GRND_RANDOM`, and `GRND_INSECURE`.
- Unknown flags return `EINVAL`.
- `buflen > IOSIZE_MAX` returns `EINVAL`.
- Zero-length requests return success with `td_retval[0] = 0`.
- `GRND_RANDOM` is accepted but not specially differentiated here.
- `GRND_INSECURE` is intentionally treated as `GRND_NONBLOCK` rather than returning pre-seeding random output.
- The file asserts `EWOULDBLOCK == EAGAIN` for Linux API compatibility naming.

## Security rationale

The comments explicitly reject producing insecure pre-seeding kernel random output, even for Linux-compatible `GRND_INSECURE`, because doing so could leak entropy about the initial seed and provide low-entropy bytes from a security-oriented API. Returning `EAGAIN` under nonblocking conditions is preferred.

## Filesystem/storage relevance

This file is not filesystem-specific. It is generic syscall infrastructure and shares the same syscall/uio/copyout style seen in file I/O paths. It matters to subset A mostly as adjacent kernel syscall plumbing, not as VFS behavior.

## Research notes

Classify as random syscall wrapper. Cross-reference with `sys_generic.c` for similar `uio` construction and `IOSIZE_MAX` validation patterns.

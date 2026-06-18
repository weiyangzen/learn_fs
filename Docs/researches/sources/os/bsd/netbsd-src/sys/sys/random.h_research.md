# File Research: sources/os/bsd/netbsd-src/sys/sys/random.h

## Purpose
Defines NetBSD `getrandom` flags and kernel/user entry points.

## Main API
- Flags: `GRND_NONBLOCK`, `GRND_RANDOM`, `GRND_INSECURE`.
- Kernel function: `dogetrandom`.
- Userland function: `getrandom`.

## Dependencies
Includes `sys/cdefs.h` and machine ANSI typedef hooks for `size_t`/`ssize_t`.

## Risks and Notes
`GRND_INSECURE` explicitly requests output without normal security readiness guarantees. Kernel implementation takes a `struct uio *`, while userland receives a byte count or error via `ssize_t`.

# File Research: sources/os/bsd/netbsd-src/lib/libc/compat-43/sethostid.c

## Scope

Compatibility implementation of `sethostid()`.

## Behavior

- Casts the provided `long hostid` to `int`.
- Writes `CTL_KERN.KERN_HOSTID` through `sysctl`.
- Returns `-1` on failure, `0` on success.

## Dependencies And Invariants

- Depends on `<sys/sysctl.h>` and kernel permission checks for setting host ID.
- Truncates to the historical 32-bit host ID representation.

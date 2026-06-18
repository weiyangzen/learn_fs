# File Research: sources/os/bsd/netbsd-src/lib/libc/compat-43/gethostid.c

## Scope

Compatibility implementation of `gethostid()`.

## Behavior

- Reads `CTL_KERN.KERN_HOSTID` through `sysctl`.
- Returns `-1` if `sysctl` fails; otherwise returns the integer host ID as `long`.

## Dependencies And Invariants

- Depends on `<sys/sysctl.h>` and kernel `KERN_HOSTID`.
- Host ID is treated as a 32-bit integer despite the `long` return type.

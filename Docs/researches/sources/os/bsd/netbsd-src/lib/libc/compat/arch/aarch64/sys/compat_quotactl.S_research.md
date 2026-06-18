# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/aarch64/sys/compat_quotactl.S

## Scope

AArch64 compatibility wrapper for `quotactl`.

## Behavior

- Emits a warning reference recommending `<sys/quota.h>`.
- Defines `PSEUDO(quotactl,compat_50_quotactl)`.

## Dependencies And Invariants

- Routes legacy libc symbol to the NetBSD 5.0-compatible quota syscall.

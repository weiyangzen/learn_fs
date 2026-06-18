# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/sh3/sys/compat_Ovfork.S

Implements SH3 compatibility `vfork`.

It uses `trapa #0x80` with `SYS_vfork`, interprets `r1` as parent/child indicator, and masks `r0` so the child returns zero and the parent returns the child pid.

Errors jump to `CERROR`.

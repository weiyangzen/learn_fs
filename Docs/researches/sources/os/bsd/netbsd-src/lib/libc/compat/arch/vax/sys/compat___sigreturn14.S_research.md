# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/vax/sys/compat___sigreturn14.S

Defines VAX compatibility `__sigreturn14`.

It maps `__sigreturn14` to `compat_16___sigreturn14` and adjusts the profiling `ENTRY` macro under `GPROF` to preserve registers.

This supports VAX legacy signal return.

# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/vax/sys/compat_sigreturn13.S

Defines VAX compatibility `sigreturn`.

It maps `sigreturn` to `compat_13_sigreturn13` and includes profiling safeguards that preserve registers under `GPROF`.

This is legacy signal-return ABI support.

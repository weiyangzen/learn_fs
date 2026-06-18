# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/sys/__m68k_read_tp.S

This tiny wrapper defines `__m68k_read_tp`. It invokes the `_lwp_getprivate` syscall and returns the result in both `%d0` and `%a0`.

It is a machine-specific thread-pointer accessor for m68k TLS/runtime code. There is no explicit error path, reflecting the expectation that reading the private LWP value is a non-failing primitive.

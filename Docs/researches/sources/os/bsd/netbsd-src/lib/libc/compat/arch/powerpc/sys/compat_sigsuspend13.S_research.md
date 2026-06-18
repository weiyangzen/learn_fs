# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/powerpc/sys/compat_sigsuspend13.S

Implements PowerPC compatibility `sigsuspend`.

It loads the integer mask from the caller-provided pointer, invokes `compat_13_sigsuspend13`, and always branches to `__cerror` because successful return is not expected.

This is old signal-mask compatibility glue.

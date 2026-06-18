# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/arm/sys/__clone.S

This ARM `__clone` wrapper validates that the function and child stack are non-null, places the function pointer and argument on the child stack, and invokes the `__clone` syscall with `(flags, stack)`. The parent returns the child pid; the child pops the function and argument, calls the function, and passes its return value to `_exit`. Null inputs branch to `__cerror` with `EINVAL`.

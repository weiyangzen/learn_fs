# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/hppa/sys/__clone.S

This HPPA `__clone` wrapper validates function and stack arguments, builds a child stack frame containing the function and argument, then invokes the `__clone` syscall with `(flags, stack)`. The parent returns normally; the child reloads the function and argument from its stack, calls through `$$dyncall`, and exits with the function's return value.

# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/mips/sys/__clone.S

This file implements MIPS `__clone` and weak `clone`. It validates function and stack arguments, places the function pointer and argument on the child stack, invokes the `__clone` syscall with `(flags, stack)`, and separates parent from child using the kernel secondary return value.

The child reloads the function and argument from its stack, sets a terminating frame, calls the function, then tail-calls `_exit` with the function’s return value. The wrapper is sensitive to MIPS call frames, GP preservation, and PIC return mechanics.

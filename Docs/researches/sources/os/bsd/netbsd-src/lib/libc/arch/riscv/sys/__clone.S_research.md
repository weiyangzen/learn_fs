# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/riscv/sys/__clone.S

This file implements RISC-V `__clone` and weak `clone`. It validates function and stack pointers, reserves space on the child stack, stores the function pointer and argument there, calls kernel `__clone(flags, stack)`, and distinguishes parent from child using the secondary return value.

In the child it loads the function and argument from the new stack, stores zero in the saved return-address frame slot, calls the function, and tail-calls `_exit` with the result. The wrapper is sensitive to RISC-V stack frame layout and register calling convention.

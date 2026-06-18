# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/aarch64/sys/__clone.S

AArch64 libc wrapper for `__clone` and weak `clone`.

Key behavior:
- Validates function pointer and child stack pointer are non-null; otherwise reports `EINVAL` through `__cerror`.
- Pushes the child argument and function pointer onto the child stack.
- Reorders arguments for the kernel `__clone(flags, stack)` syscall.
- On parent return, returns child pid.
- On child return, pops function/argument from the stack, calls the function, and passes its return value to `_exit`.

Dependencies:
- AArch64 syscall macros in `SYS.h`.
- Kernel fork-style return convention using `x1` to distinguish parent/child.

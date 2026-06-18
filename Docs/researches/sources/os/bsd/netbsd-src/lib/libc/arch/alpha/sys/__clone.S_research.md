# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/alpha/sys/__clone.S

Alpha libc wrapper for `__clone` and weak `clone`.

Key behavior:
- Validates function pointer and stack pointer, returning `EINVAL` through `__cerror` if either is null.
- Stores the child function and argument on the child stack.
- Reorders arguments so the syscall receives `(flags, stack)`.
- Calls `__clone` through `CALLSYS_ERROR`.
- Parent returns child pid.
- Child loads function/argument from the new stack, calls the function, then calls `_exit` with its return value.

Dependencies:
- Alpha syscall return convention using `a4` as second return value/child discriminator.
- `SYS.h` and Alpha GP setup macros.

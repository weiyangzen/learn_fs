# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/vax/sys/getcontext.S

## Summary
Implements VAX `_getcontext()` with weak `getcontext` alias.

## Key Details
- Calls `SYS_getcontext`.
- Rewrites the caller frame so execution resumes at local label `2`.
- Updates saved AP, SP, FP, and PC fields in the ucontext.
- Clears `%r0` before returning to the original caller.

## Notes
The implementation avoids using `%r4` and `%r5` because they are needed by pthread switch code.

# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/alpha/sys/__vfork14.S

Alpha wrapper for versioned `vfork`.

Key behavior:
- Calls `SYSCALL(__vfork14)`.
- Uses `cmovne a4, zero, v0` so child return value becomes zero while parent keeps child pid.
- Returns to caller.

Dependencies:
- Alpha fork/vfork return convention using `a4`.

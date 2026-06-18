# File Research: sources/os/bsd/netbsd-src/sys/sys/sigtypes.h

Read completely: 125 lines.

This header defines signal-related base types and signal-set manipulation macros. `sigset_t` is four 32-bit words, supporting up to 128 bit positions, and macros implement mask, word selection, add, delete, membership, empty/fill, equality, union, subtraction, and intersection.

Under POSIX/XOpen/NetBSD feature modes it also defines `stack_t`/`struct sigaltstack` with stack pointer, size, and flags.

Risks: the macros do not validate signal numbers. Out-of-range signal values can index beyond the intended words if callers do not check first.

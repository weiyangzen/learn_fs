# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc64/sys/__sigtramp2.S

This file implements the PowerPC64 signal trampoline `__sigtramp_siginfo_2`. The kernel enters with `%r30` pointing to the ucontext, so the trampoline moves `%r30` to `%r3`, invokes `setcontext`, and invokes `exit` if restoration fails.

Unlike 32-bit PowerPC’s version, this file does not include extensive `.cfi` unwind metadata. Its runtime role remains signal context restoration.

# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/aarch64/sys/__sigtramp2.S

AArch64 signal trampoline used for returning from signal handlers.

Key behavior:
- Defines DWARF CFI for a signal frame, with CFA based on `x28` pointing into the ucontext general-register area.
- Records offsets for AArch64 general registers and the signal-return pseudo-register.
- Includes a `nop` before the trampoline so unwinding with return-PC-minus-one resolves correctly.
- `__sigtramp_siginfo_2` moves `x28` into `x0`, calls `setcontext`, and if that fails calls `exit` with the error code.

Dependencies:
- Generated `assym.h` offsets.
- Kernel signal frame contract and `setcontext` syscall.

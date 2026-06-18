# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/alpha/sys/__sigtramp2.S

Alpha signal trampoline used to return from signal handlers.

Key behavior:
- Defines DWARF CFI for an Alpha signal frame based on `sp + sizeof(siginfo_t) + UC_GREGS`.
- Records offsets for general registers and the signal-return pseudo-register.
- Includes a pre-trampoline `nop` for return-PC-minus-one unwinding.
- `__sigtramp_siginfo_2` loads GP, points `a0` at the ucontext after the siginfo, calls `setcontext`, and if that fails exits with code `-1`.

Dependencies:
- Generated `assym.h` offsets.
- Alpha signal frame layout and `setcontext` syscall.

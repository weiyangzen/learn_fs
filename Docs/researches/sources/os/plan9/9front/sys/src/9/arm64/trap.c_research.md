# File Research: sources/os/plan9/9front/sys/src/9/arm64/trap.c

ARM64 trap, syscall, fault, notify, process-register, and dump support.

Key behavior:
- Allocates and patches the ARM64 vector table with the template stubs from `l.s`.
- Classifies ESR exception classes and handles aborts, FP traps, IRQs, FIQs, SError, and unhandled traps.
- Enters/exits kernel accounting and FPU protection around traps and syscalls.
- Implements syscall dispatch through `dosyscall`.
- Builds user notification frames and validates `noted` resume modes.
- Handles translation/access/permission faults via generic `fault`.
- Saves/restores TPIDR_EL0 and FPU state across process switches.
- Sets up kernel and fork child scheduler contexts.
- Dumps registers and kernel stack PCs for diagnostics.

Dependencies:
- Uses `syswr`, `irq/fiq`, FPU helpers, process/note/fault machinery, and assembly symbols.

Research notes:
- Kernel faults inside `peek` are specially recovered by redirecting PC to link.
- User-modifiable PSR bits are masked in `setregisters`.

# File Research: sources/os/plan9/9front/sys/src/9/pc64/fpu.c

amd64 floating-point, SSE, and AVX state management for kernel and user contexts.

Key behavior:
- Selects FPU save/restore backends at CPU initialization: FXSAVE/FXRSTOR or XSAVE/XSAVEOPT/XSAVES when CPUID and `*noavx` allow AVX state.
- `fpinit` initializes x87 control word and MXCSR defaults.
- Trap handlers convert x87/SIMD faults into user notes or kernel panics with decoded exception messages.
- `mathinit` registers math, coprocessor-not-available, coprocessor-overrun, and SIMD trap handlers.
- Uses lazy FPU activation: `mathemu` handles device-not-available traps by allocating/restoring state on first use.
- Process hooks save, restore, fork, clear, and free user FPU state across scheduler and process lifecycle events.
- `fpukenter` and `fpukexit` protect user FPU state and allow kernel code, traps, and interrupts to use floating-point/vector state safely.
- Note handling functions manage nested saved FPU contexts for Plan 9 note delivery.

Notable dependencies:
- Assembly helpers in `l.s`: `_clts`, `_stts`, `_fxsave`, `_fxrstor`, `_xsave`, `_xrstor`, `_xsaveopt`, `_xsaves`, `_fwait`, `_ldmxcsr`.
- Trap registration, process structures, and Plan 9 notes.

Research notes:
- The code maintains separate user and kernel FPU state stacks per process, plus per-machine state for interrupt context.
- Allocation loops can wait for memory when running in process context.
- `fpcheck` intentionally checks pending unmasked exceptions before restoring a saved state.

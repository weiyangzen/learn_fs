# File Research: sources/os/plan9/9front/sys/src/9/ppc/trap.c

PowerPC C-level trap, interrupt, syscall, notification, and register-debug handling.

Key responsibilities:
- Manages interrupt vector handler registration/removal through `intrenable()` and `intrdisable()`, delegating hardware vector enable/disable to board code.
- Classifies exceptions and dispatches external interrupts, decrementer interrupts, page faults, TLB misses, syscalls, floating-point unavailable traps, program exceptions, and unexpected traps.
- Restores/lazily initializes user floating-point state and controls MSR FP enable.
- Converts user faults/traps into notes and panics on kernel faults.
- Installs low-level exception vectors with `sethvec()`/`setmvec()`.
- Provides floating-point exception name formatting, stack dump, register dump, kernel-process child setup, exec/fork register setup, debug PC access, and register replacement helpers.
- Implements PowerPC syscall entry/exit around `dosyscall()`, notification delivery (`notify()`), and note return (`noted()`).

Dependencies:
- Pairs with assembly trap entry/return in `l.s`, board vector logic, shared Plan 9 syscall/note/fault/process code, and PPC `Ureg` layout.

Notable behavior:
- `notify()` lays a copied `Ureg` plus message on the user stack and sets the user PC to `up->notify`.
- `noted()` preserves privileged status bits through `setregisters()` and re-applies FP enable based on process FP state.

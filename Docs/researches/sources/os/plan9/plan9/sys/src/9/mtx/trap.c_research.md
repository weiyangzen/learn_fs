# File Research: sources/os/plan9/plan9/sys/src/9/mtx/trap.c

Implements MTX PowerPC trap dispatch, interrupt registration, syscall entry, FP unavailable handling, user notification, and debug register utilities.

Key points:
- `hwintrinit()` initializes the 8259 and enables MPIC vector 0 as the 8259 cascade.
- `intrenable()`/`intrdisable()` allocate and manage `Vctl` chains per vector, routing PCI IRQs through MPIC and non-PCI IRQs through the 8259 offset vector range.
- `trap()` decodes PowerPC exception code from `ureg->cause`, distinguishes user/kernel mode, dispatches external interrupts, decrementer clock interrupts, syscalls, FP unavailable traps, instruction/data faults, and program exceptions.
- FP unavailable traps lazily restore either the initial FP state or the proc’s saved FP state and set `MSR_FP`.
- `faultpower()` calls portable `fault()` and posts debug notes or panics depending on user/kernel context.
- `sethvec()` writes low exception-vector stubs that branch to handler code, using either direct branch or LR sequence if target is too far; `trapinit()` installs `trapvec` for vectors up to `0x2000`.
- `intr()` acknowledges MPIC, cascades vector 0 through `i8259intack()`, calls all registered handlers, issues EOI, and preempts if a proc is active.
- Provides stack/register diagnostics: `callwithureg()`, `dumpstack()`, `dumpregs()`, `setkernur()`, and `dbgpc()`.
- Defines process entry helpers: `kprocchild()`, `execregs()`, `forkchild()`, `userpc()`, and `setregisters()`.
- `syscall()` reads syscall number from `r3`, copies `Sargs` from user stack, calls `systab`, handles Plan 9 error stacks, returns in `r3`, and performs note delivery.
- `notify()` and `noted()` implement Plan 9 user note delivery/restoration on PowerPC user stacks.

Dependencies and interactions:
- Uses `raven.c` MPIC hooks, i8259 hooks, `clockintr()`, `fault()`, `systab`, `sysctab`, and process/note machinery.
- Assumes PowerPC `Ureg` layout and `mem.h` exception/MSR constants.
- Trap vectors call assembly `trapvec`.

Research relevance:
- Central exception, interrupt, syscall, and user-notification path for the MTX kernel.

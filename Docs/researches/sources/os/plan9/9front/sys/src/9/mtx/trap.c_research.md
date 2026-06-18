# File Research: sources/os/plan9/9front/sys/src/9/mtx/trap.c

This file implements MTX PowerPC trap, interrupt, fault, syscall, note, register, and debug support. It also owns the platform interrupt handler registry and hardware interrupt enabling/disabling logic across MPIC and 8259.

`hwintrinit` initializes the 8259 and routes it through MPIC vector 0. `intrenable` allocates `Vctl`, enables the hardware vector via MPIC or PIC, and chains handlers; `intrdisable` removes matching handlers and disables hardware when no handlers remain. `intr` acknowledges MPIC, handles 8259 cascades, invokes registered handlers, and runs EOI callbacks.

`trap` decodes PowerPC exception vectors. It handles external interrupts, decrementer interrupts, syscalls, floating-point unavailable traps, instruction/data faults, program exceptions, and default user/kernel traps. User faults become notes or call `faultpower`; kernel faults dump registers and panic.

The file also installs exception vectors with `trapinit`/`sethvec`, implements stack/register dumping, process child setup, `evenaddr`, `execregs`, `forkchild`, user PC helpers, register setting, `syscall`, `notify`, and `noted`.

Filesystem relevance is very high: syscalls, page faults, user notes, interrupts, and device completions all pass through this file.

Notable risks: syscall is implemented in C within this trap file rather than a separate assembly entry; FP state checks include debug prints; interrupt vector chaining requires compatible ISR/EOI callbacks for shared vectors.

# File Research: sources/os/plan9/9front/sys/src/9/omap/trap.c

OMAP interrupt controller, exception, fault, and trap handling.

Key behavior:
- Defines OMAP MPU INTC register layout and 96 IRQ vectors.
- `trapinit` copies high-vector stubs, installs banked stacks, masks all interrupts, sets priorities, and marks IRQ setup ready.
- `irqenable`/`irqdisable` manage per-IRQ handler lists and mask/unmask INTC lines.
- `irq` reads active IRQ, dispatches all handlers on that vector, masks unexpected interrupts, accounts interrupt timing, and acknowledges INTC.
- `faultarm` routes user/kernel memory faults into Plan 9 fault handling or panics on unrecoverable kernel faults.
- `trap` handles IRQ, prefetch abort, data abort, and undefined-instruction exceptions, including breakpoint notes, memory fault decoding, external abort panics, and soft-FPU emulation.
- `probeaddr` safely probes a physical/virtual address by using trap recovery.
- Dump helpers print stack, GPRs, and CP15 system-control registers.

Research notes:
- Data-fault status decoding uses ARMv7 extended FSR bits and distinguishes translation, permission, alignment, domain, external abort, and parity cases.
- Undefined user instructions are offered to `fpiarm`; unhandled cases become debug notes.

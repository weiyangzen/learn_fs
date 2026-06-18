# File Research: sources/os/plan9/plan9/sys/src/9/teg2/trap.c

ARM MPCore GIC v1 interrupt controller, trap, exception, and fault core.

Key behavior:
- Defines GIC distributor and CPU-interface register layouts.
- Installs high and low exception vectors from `lexception.s`.
- Sets exception-mode stack slots in `Mach`.
- Configures GIC groups, priorities, trigger modes, CPU targets, masks, pending/active state, and CPU interface.
- Provides IRQ registration/removal through `irqenable` and `irqdisable`.
- Handles IRQ dispatch, interrupt timing histograms, page faults, data abort decoding, prefetch faults, breakpoints, undefined instructions, and FPU emulation.
- Provides diagnostic register/stack dumping and `probeaddr`.

Important functions:
- `trapinit`, `trap`, `irq`, `datafault`, `faultarm`.
- `intcunmask`, `intcmask`, `intrcpu`, `intrshutdown`.
- `dumpregs`, `dumpstack`, `probeaddr`.

Notes:
- GIC register comments document banked-per-CPU surprises.
- Distributor `memset`/`memmove` is avoided because it can generate external aborts.

# File Research: sources/os/plan9/9front/sys/src/9/mt7688/irq.c

This file implements interrupt routing for the MT7688 port. It maps Plan 9 IRQ numbers to MT7688 secondary interrupt-controller lines with `irq2inc` and back with `inc2irq`.

`intrinit` masks all secondary interrupts and registers `incintr` on CPU interrupt `IRQlow`. `intrenable` installs one or more handlers per IRQ, enables CPU interrupt bits directly for CPU-local IRQs, and programs `FIQ_SEL` plus `IRQ_MASK_SET` for SoC-controller IRQs. `intrdisable` masks the reverse path.

`intr(Ureg*)` is called by trap handling for CPU interrupts. It accounts for clock interrupts on `INTR7`, dispatches CPU-level handler chains for `INTR2` through `INTR6`, and reports unhandled pending bits. `incintr` reads `IRQ_STAT` or `FIQ_STAT`, walks secondary interrupt bits, invokes registered handlers, and reports unhandled secondary interrupts. `intrclear` writes `IRQ_EOI`.

Filesystem relevance is indirect: this is the dispatch path for UART, Ethernet, USB, storage, and timer interrupt handlers. A storage or network filesystem workload depends on reliable interrupt masking, acknowledgment, and handler chaining here.

Notable risks: high-priority `IRQhigh` registration is commented out; handler arrays are indexed by assumed IRQ layout; unhandled secondary interrupts are printed and delayed but not otherwise recovered.

# File Research: sources/os/plan9/plan9/sys/src/9/omap/trap.c

OMAP trap, interrupt-controller, exception, fault, register dump, and probe-address implementation.

Key responsibilities:
- Defines the OMAP35 MPU interrupt controller register map and interrupt handler chain `Vctl`.
- `trapinit()` installs high vectors, initializes per-mode stacks, masks all interrupts, and initializes interrupt priorities.
- Provides interrupt mask/unmask/save/restore helpers and `intrsoff`.
- `irqenable()`/`irqdisable()` manage chained handlers per IRQ and controller masking.
- `irq()` dispatches active IRQs, handles unexpected interrupts, tracks interrupt timing, and acknowledges the controller.
- `trap()` handles IRQ, prefetch abort, data abort, and undefined instruction exceptions.
- `faultarm()` dispatches VM faults to generic `fault()` and posts notes/panics on failure.
- Supports breakpoint handling, external abort decoding, alignment/access/permission fault handling, and soft-float emulation through `fpiarm`.
- Provides register/stack dumps and CP15 status dumps.
- `probeaddr()` safely attempts a kernel load, converting a fault into `-1` through the trap probing path.

Important behavior:
- Adjusts exception PC by `-4`, or `-8` for data aborts, before decoding.
- Clears `ldrexvalid` around interrupts/exceptions.
- Clock interrupt detection is IRQ number range 37-47.
- Unknown/unhandled interrupts are masked.
- Kernel faults generally panic; user faults become Plan 9 debug notes.
- Undefined user instructions first check the Plan 9 breakpoint encoding, then try floating-point emulation.

Dependencies:
- Depends on `lexception.s` vectors, interrupt controller physical address from `mem.h`, CP15 helpers from `l.s`, VM fault path, process note path, and `Ureg` layout.

Notable risks:
- Fault-status decoding is ARM-specific and panics on many external/parity cases.
- Probe handling depends on global `probing/trapped` state protected by a lock.
- IRQ handler invariants require handlers not to lower interrupt priority.

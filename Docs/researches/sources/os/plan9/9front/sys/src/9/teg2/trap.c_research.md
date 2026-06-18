# File Research: sources/os/plan9/9front/sys/src/9/teg2/trap.c

ARM GIC v1 setup, IRQ dispatch, exception handling, and diagnostics.

Purpose:
- Initializes exception vectors and Tegra ARM interrupt controller state.
- Dispatches IRQ handlers, handles data/prefetch faults, undefined instructions, syscall aftermath, and kernel/user notifications.

Key behavior:
- Defines GIC distributor and CPU interface register layouts.
- `trapinit` copies vector code to high and low vector pages, sets exception-mode stack save areas, verifies ARM GIC IDs, configures priorities/targets, and enables distributor/CPU interface.
- `irqenable` and `irqdisable` manage `Vctl` chains and mask/unmask interrupts.
- `irq` acknowledges, dispatches, dismisses, masks unexpected IRQs, and records service-time histograms.
- `datafault` decodes ARM fault status and routes translation/permission faults to VM `fault`.
- `probeaddr` uses a `m->probing` flag to turn selected kernel data aborts into `-1`.

Integration:
- Works with `lexception.s` frame construction and `mmu.c` mappings.
- Exposes IRQ APIs used by UART, PCI, timer, and other device drivers.

Risks/notes:
- Uses direct MMIO register writes instead of bulk memory ops because comments report distributor-register aborts.
- `irqtooearly` blocks premature IRQ registration until kernel memory/device init is ready.

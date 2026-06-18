# File Research: sources/os/plan9/9front/sys/src/9/lx2k/gic.c

LX2K GICv3 interrupt controller driver. It defines GIC distributor and redistributor register offsets, locates the redistributor for each CPU, initializes interrupt groups/priorities/targets, enables the CPU interface, dispatches IRQ/FIQ interrupts, and maps PCI interrupts through the PCI layer.

`intrinit` disables/clears the distributor on CPU 0, resets SPI configuration, initializes SGI/PPI redistributor state for the current CPU, then enables ICC group 1 handling. `irq` reads `ICC_IAR1_EL1`, ignores spurious IDs, dispatches matching `Vctl` handlers, marks clock interrupts, and EOIs through `ICC_EOIR1_EL1`.

`intrenable` supports normal IRQs, a special FIQ path, PPI/SPI enablement, priority programming, CPU target selection, and PCI delegation when the TBDF is a PCI bus value. `intrdisable` only delegates PCI disable and otherwise does not remove normal GIC handlers.

Notable risks: handler chains are bucketed by `intid % 32`; non-PCI `intrdisable` is effectively unimplemented; SPI targeting assumes CPU 0.

# File Research: sources/os/plan9/9front/sys/src/9/imx8/gic.c

Role: GICv3 interrupt controller driver for i.MX8, including distributor, redistributor, CPU interface, shared interrupt dispatch, FIQ, and PCI interrupt forwarding.

Key responsibilities:
- Defines GICD/GICR register offsets and stores interrupt handlers in per-CPU hash buckets by `intid % 32`.
- Locates each CPU redistributor by matching `GICR_TYPER` affinity bits.
- Disables CPU interrupt groups and the distributor during shutdown.
- Initializes distributor on CPU 0: clears/enables groups, disables/clears interrupts, priorities, targets, configs, then enables distributor groups.
- Initializes per-CPU redistributor state and CPU interface registers.
- `irq()` reads `ICC_IAR1_EL1`, skips spurious IDs, calls matching handlers, notes clock IRQ, and writes EOI.
- `fiq()` dispatches a single registered FIQ handler on CPU 0.
- `intrenable()` routes PCI `tbdf` interrupt requests to `pciintrenable()`, otherwise allocates a `Vctl`, chooses CPU target, enables ICC group 1, and enables GICR/GICD interrupt.
- `intrdisable()` delegates PCI disables and otherwise has no non-PCI removal logic.

Dependencies:
- ARM64 system registers, `sysrd/syswr`, PCI shim, Plan 9 `Vctl`-style interrupt interface.

Notes and risks:
- Non-PCI `intrdisable()` does not remove handlers or mask GIC lines.
- FIQ registration uses special `IRQfiq` and a single global `vfiq`.

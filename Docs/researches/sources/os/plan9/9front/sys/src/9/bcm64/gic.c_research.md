# File Research: sources/os/plan9/9front/sys/src/9/bcm64/gic.c

ARM Generic Interrupt Controller support for BCM ARM64 kernels.

Key responsibilities:
- Maps distributor and CPU-interface registers using `CBAR_EL1`.
- Disables CPU interface and distributor during shutdown.
- Clears/enables interrupts and initializes priorities/targets.
- Dispatches IRQ handlers by GIC interrupt ID.
- Handles FIQ through a dedicated handler.
- Bridges PCI MSI interrupt enable/disable through PCI helpers.
- Translates legacy BCM IRQ numbers to GIC interrupt IDs.

Important behavior:
- Per-CPU private interrupts are stored by current CPU; shared interrupts target CPU0 unless otherwise selected.
- Clock interrupt detection includes system and generic timer IRQs.
- FIQ handler is restricted to CPU0.

Dependencies:
- ARM64 system registers, PCI interrupt helpers, Plan 9 interrupt API, trap code, and SoC local interrupt layout.

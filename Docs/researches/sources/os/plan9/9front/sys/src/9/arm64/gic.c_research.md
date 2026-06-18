# File Research: sources/os/plan9/9front/sys/src/9/arm64/gic.c

ARM64 Generic Interrupt Controller support for QEMU virt-style GIC.

Key behavior:
- Defines distributor and redistributor register offsets.
- Finds per-CPU redistributor by matching `GICR_TYPER`.
- Initializes the distributor on CPU 0, clears/enables groups, priorities, targets, and configurations.
- Initializes per-CPU SGI/PPI redistributor state.
- Enables the CPU interface through ICC system registers.
- Dispatches IRQs and FIQs through registered `Vctl` handlers.
- Routes PCI interrupt registration to `pciqemu.c`.

Dependencies:
- Uses `VIRTIO`, interrupt constants from `io.h`, ICC system registers, and PCI helpers.

Research notes:
- SPI interrupts are targeted at CPU 0; SGI/PPI interrupts stay per-CPU.
- `intrdisable` only delegates PCI removal and does not remove non-PCI `Vctl` entries.

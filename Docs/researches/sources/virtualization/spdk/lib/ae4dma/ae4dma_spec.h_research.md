# File Research: sources/virtualization/spdk/lib/ae4dma/ae4dma_spec.h

`ae4dma_spec.h` captures AE4DMA hardware-facing constants, descriptor layout, status values, queue status values, and queue register layout.

It defines 16 hardware queues, 32 descriptors per queue indirectly via the internal header, queue enable bits, common config offset, PCI BAR index, descriptor status enum values, and hardware queue status enum values.

The AE4DMA command descriptor is exactly 32 bytes: control/timestamp dword, status/error/id dword, length, reserved, source low/high, and destination low/high. A static assertion enforces this size.

The per-queue register block includes control, status, max index, read index, write index, interrupt status, and queue-base low/high registers. The register structure is packed/aligned for MMIO access.

Research notes: descriptor field order and register layout are hardware ABI. Any change must match the AE4DMA device specification and the MMIO programming in `ae4dma.c`.

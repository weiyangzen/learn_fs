# File Research: sources/os/plan9/9front/sys/src/9/port/virtio10mem.c

Memory-mapped register access implementation for Virtio 1.0 PCI capabilities.

Key responsibilities:
- Implements `vin8/16/32/64()` and `vout8/16/32/64()` as direct volatile-like loads/stores into `Vio_mem`.
- Implements `virtiounmap()` using `vunmap()`.
- Implements `virtiomapregs()` by reading the PCI capability BAR, offset, and length fields, validating that the region is memory space and within the BAR size, and mapping it with `vmap()`.

Dependencies:
- Uses Plan 9 PCI config accessors and virtual memory mapping.

Notable behavior:
- Rejects I/O BARs; this file is only for memory-backed virtio config regions.

# File Research: sources/os/plan9/9front/sys/src/9/pc/virtio10pc.c

PC-specific VirtIO 1.0 register mapping and typed register I/O helpers.

Key behavior:
- `vin8`, `vin16`, `vin32`, and `vin64` read VirtIO registers through either I/O ports or memory-mapped registers depending on `Vio.type`.
- `vout8`, `vout16`, `vout32`, and `vout64` write through the same abstraction.
- `virtiounmap` releases either an I/O port allocation or a VM mapping.
- `virtiomapregs` decodes a VirtIO PCI capability’s BAR, offset, and length, validates the requested size against the PCI BAR, and maps it as `Vio_port` or `Vio_mem`.

Notable dependencies:
- VirtIO 1.0 definitions from `../port/virtio10.h`.
- PCI config-space helpers and PC I/O allocation/mapping functions.

Research notes:
- 64-bit port I/O is implemented as two 32-bit reads/writes.
- The I/O allocation label is hardcoded as `"ethervirtio10"`, reflecting its likely original network-driver use even though the helper is generic.

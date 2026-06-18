# File Research: sources/os/bsd/dragonflybsd/sys/sys/bus_resource.h

Read completely: 46 lines.

This header defines generic bus resource type IDs.

Key contents:
- `SYS_RES_IRQ` for interrupt lines.
- `SYS_RES_DRQ` for ISA DMA lines.
- `SYS_RES_MEMORY` for memory-mapped I/O.
- `SYS_RES_IOPORT` for I/O ports.

Security/reliability notes:
- No runtime logic. These constants are part of driver resource allocation ABI.

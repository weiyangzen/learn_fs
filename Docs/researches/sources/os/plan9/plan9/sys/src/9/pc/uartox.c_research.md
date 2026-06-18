# File Research: sources/os/plan9/plan9/sys/src/9/pc/uartox.c

Purpose: `PhysUart` driver named `OXPCIe95x` for Oxford Semiconductor OXPCIe95x PCIe multiport UARTs.

Main structures:
- `Ctlr`: PCI device, mapped MMIO registers, interrupt mask, name, and up to 16 ports.
- `Port`: embeds `Uart`, points to controller and per-port MMIO window, tracks FIFO trigger level and modem output state.

Key logic:
- `oxpnp` scans Oxford vendor `0x1415` devices, recognizes OXPCIe952/954/958 IDs, maps BAR0, reads UART count, creates one `Port` per UART, and chains them into the UART list.
- `oxenable` registers the shared interrupt when first port is enabled, enables per-port interrupt mask, enters 950 enhanced mode, enables Rx status/THRE/Rx-ready interrupts, asserts DTR/RTS, and enables FIFO.
- `oxdisable` drops DTR/RTS, disables FIFO and per-port interrupts, and unregisters the shared IRQ when no ports remain enabled.
- `oxinterrupt` checks global interrupt status and handles receive, transmit-empty, and modem-status events for enabled ports.
- `oxkick` writes staged output while THR empty.
- `oxbaud` supports standard baud rates by programming table-derived DLM/DLL values.
- `oxbits`, `oxstop`, `oxparity`, `oxmodemctl`, `oxrts`, `oxdtr`, `oxdobreak`, `oxstatus`, and `oxfifo` implement UART operations.

Dependencies and integration:
- Implements Plan 9 `PhysUart oxphysuart`.
- Uses PCI/MMIO mapping, interrupt registration, and `devuart` helpers.

Risks and notes:
- Baud support is limited to explicit table values from the device datasheet.
- The interrupt handler uses a single interrupt-status read per port and does not loop until all pending causes are drained.
- FIFO support is tailored to 950-mode 128-byte FIFOs and only controls receive trigger levels.

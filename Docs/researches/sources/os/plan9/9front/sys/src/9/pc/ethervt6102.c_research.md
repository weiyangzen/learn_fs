# File Research: sources/os/plan9/9front/sys/src/9/pc/ethervt6102.c

Implements the Plan 9/9front Ethernet driver for VIA VT6102 Rhine II and compatible Rhine III PCI Fast Ethernet controllers. It registers as both `vt6102` and `rhine`.

Key elements:
- Defines I/O register offsets, control/status bits, descriptor status bits, and FIFO/DMA threshold constants for the Rhine device family.
- Uses a `Ds` descriptor structure whose first four fields are hardware-visible: `status`, `control`, `addr`, and `branch`; software fields track `Block`, bounce buffers, and ring links.
- Maintains `Ctlr` state for PCI identity, port I/O base, RX/TX descriptor rings, interrupt mask state, MII link state, counters, and TX alignment statistics.
- `vt6102pci()` scans PCI Ethernet devices for VIA IDs `0x1106:0x3065` and `0x1106:0x3106`, allocates I/O space, enables PCI, resets hardware, and links controllers into a global list.
- `vt6102reset()` performs device detach/reset, reloads EEPROM MAC address, configures DMA and RX/TX thresholds, accepts broadcast/multicast traffic, and initializes generic MII support.
- `vt6102attach()` allocates aligned RX/TX descriptor memory, RX buffers, and per-TX bounce buffers, then programs RX/TX descriptor base registers and starts the device.
- `vt6102transmit()` reclaims completed TX descriptors, handles TX engine stop cases after abort/underflow, aligns outgoing packets using a small bounce prefix when needed, and kicks transmit demand.
- `vt6102receive()` consumes RX descriptors, accounts receive errors, strips Ethernet CRC, delivers packets with `etheriq()`, and replants buffers.
- `vt6102interrupt()` disables interrupts while servicing, handles link state change, RX, TX, and underflow conditions, dynamically raises TX FIFO threshold on underflow, and reenables the adjusted mask.
- `vt6102lproc()` sleeps on link-change interrupts, polls MII status, and updates full-duplex control.
- `vt6102ifstat()` exposes driver counters, threshold values, and PHY registers.

Filesystem relevance: none directly. This is kernel network hardware support, but it demonstrates Plan 9 driver patterns: PCI probing, DMA-safe descriptor rings, interrupt masking, MII PHY integration, kernel process link management, and `Ether` callback registration.

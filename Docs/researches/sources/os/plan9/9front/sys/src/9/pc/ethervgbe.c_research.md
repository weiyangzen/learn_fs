# File Research: sources/os/plan9/9front/sys/src/9/pc/ethervgbe.c

Implements a Plan 9 driver for VIA Velocity VT6122 gigabit Ethernet.

Key behavior:
- Defines VIA Velocity I/O registers, command/status bits, MII registers, CAM filter registers, RX/TX descriptor formats, interrupt bits, and debug controls.
- Probes PCI class Ethernet device `0x1106:0x3119`, requires I/O BAR0 of size 256, allocates the I/O range, and registers as `vgbe`.
- Performs soft reset, EEPROM reload, MAC address read, interrupt setup, 32-bit DMA address setup, MAC start, RX/TX engine enable, and MII bus initialization.
- Allocates 256 RX and 256 TX descriptors, plants RX blocks from a `Bpool`, loads descriptor base/count/index registers, and starts RX/TX queues on attach.
- RX interrupt path scans all RX descriptors, delivers good frames minus CRC, replants descriptors, and wakes the RX queue.
- TX path finds free descriptors near the hardware TX index, dequeues from `edev->oq`, writes one-fragment TX descriptors, wakes the queue, and frees completed blocks on TX completion.
- Link status uses PHY status register to set 10/100/1000 speed and link state.
- Multicast path programs up to 32 CAM entries and CAM mask bits; promiscuous mode toggles RX control bits.
- Provides ctl commands `reset`, `dumpintr`, `dumprx`, `dumptx`, and `dumpall`, plus `ifstat` counters.

Dependencies:
- Uses Plan 9 PCI, I/O ports, Ethernet, MII, block pool, command parsing, and interrupt APIs.
- Uses little-endian identity macros, so the code assumes a little-endian host.

Research notes:
- File comments list several unfinished areas: 64/48-bit DMA, autonegotiation tuning, shutdown, jumbo frames, error reporting, and fuller promiscuous behavior.
- RX/TX descriptor scanning is simple and scans whole rings rather than maintaining software producer/consumer indices.
- Only low 32-bit DMA addresses are programmed.

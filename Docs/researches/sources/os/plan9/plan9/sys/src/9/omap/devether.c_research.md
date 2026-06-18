# File Research: sources/os/plan9/plan9/sys/src/9/omap/devether.c

Implements the generic Plan 9 Ethernet `#l` device layer for OMAP hardware drivers.

Key points:
- Maintains up to `MaxEther` registered `Ether` controllers in `etherxx[]`.
- Standard device methods delegate attach/walk/stat/open/close/read/write/bwrite/wstat to `netif` helpers and hardware callbacks.
- `etheriq()` receives packets, filters multicast/broadcast/promiscuous traffic, checks destination/source, handles bridge/headersonly modes, fans packets out to interested `Netfile`s, and can pass the original block without copy.
- `etheroq()` handles transmit accounting, loopback/broadcast/promiscuous local delivery, and queues non-loopback packets to the hardware output queue.
- `etherwrite()` handles netif control writes, `nonblocking` queue control, hardware-specific `ctl`, and packet writes with MTU checks and source MAC insertion.
- `addethercard()` registers hardware reset/probe functions by type.
- `parseether()` parses colon-separated MAC addresses.
- `etherreset()` asks `archether()` for platform devices, applies config/options, matches registered card drivers, installs interrupts, reports device info, initializes netif queues, MAC/broadcast addresses, and controller table.
- `ethershutdown()` calls hardware shutdown callbacks.
- Provides CRC helper `ethercrc()` and debug helpers `dumpoq()`/`dumpnetif()`.

Dependencies and interactions:
- Hardware drivers such as `ether9221.c` register with `addethercard()`.
- `archether()` in `archomap.c` declares available platform Ethernet hardware.
- Uses Plan 9 `netif` framework and `intrenable()`.

Research relevance:
- Hardware-independent Ethernet filesystem and packet multiplexing layer for OMAP network drivers.

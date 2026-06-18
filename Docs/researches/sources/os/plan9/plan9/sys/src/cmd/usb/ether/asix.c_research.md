# File Research: sources/os/plan9/plan9/sys/src/cmd/usb/ether/asix.c

Read fully: 489 lines, 10209 bytes. SHA-256 prefix: `2c86bc6fc1122e31`.

This file implements support hooks for ASIX USB Ethernet adapters. It contains vendor request constants, reset/GPIO/MII/media/RX-control bit definitions, controller initialization for supported chips, packet framing/unframing, promiscuous mode, multicast mode, and reset registration.

Low-level helpers issue vendor `usbcmd()` reads/writes, read GPIO/PHY/RX control/MAC/EEPROM, and access MII registers. `ctlrinit()` configures AX88178 and AX88772-like devices, including GPIO sequences, PHY selection/reset, auto-negotiation advertisement, medium mode, IPG, and RX control. Some known chips are recognized but reported unimplemented.

ASIX USB packets carry a 32-bit length/complement header. `asixbread()` reads aggregate USB data, validates the header, copies Ethernet frames into generic `Buf`s, and caches remaining aggregate data. `asixbwrite()` prepends the length/complement header and adds a zero-length-style terminator header when packet length aligns with endpoint max packet size.

Integration: plugs into the common USB Ethernet framework through `Ether` callbacks (`bread`, `bwrite`, `free`, `promiscuous`, `multicast`) and `asixreset()`.

Risk notes: comments note behavior was inferred from other systems without documentation. Multicast filtering is not implemented precisely; it toggles all-multicast when any multicast subscriptions exist. A8817x/A88179 are known but not implemented.

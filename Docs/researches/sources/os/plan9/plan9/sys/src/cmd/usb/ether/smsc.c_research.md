# File Research: sources/os/plan9/plan9/sys/src/cmd/usb/ether/smsc.c

SMSC LAN95xx backend for the generic USB Ethernet layer.

Main responsibilities:
- Defines LAN95xx USB vendor requests, device registers, MII registers, EEPROM bits, and transmit/receive header flags.
- `wr` and `rr` issue USB vendor register writes/reads.
- `miird`/`miiwr` access PHY registers through MAC MII registers.
- `eepromr` reads EEPROM bytes, and `getmac` obtains the MAC address.
- `smscinit` performs hardware reset, EEPROM MAC load, burst configuration, LED setup, VLAN/default AFC setup, checksum offload disable, PHY initialization, interrupt setup, and TX/RX enable.
- `smscbread` unpacks LAN95xx receive aggregation headers and extracts Ethernet frames.
- `smscbwrite` prepends the two LAN95xx transmit command words before writing to the bulk-out endpoint.
- `smscreset` matches `cinfo[]` entries, initializes hardware, allocates burst buffer state, installs `Etherops`, and sets a nominal 100 Mbps speed.

Notable gaps:
- Promiscuous and multicast methods are stubs returning `-1` under disabled TODO blocks.
- Link speed is hardcoded to 100 Mbps.
- Receive burst constants are conservative (`Hsburst = 8`) with a comment noting the Linux value differs.

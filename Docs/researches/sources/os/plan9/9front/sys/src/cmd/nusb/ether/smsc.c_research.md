# File Research: sources/os/plan9/9front/sys/src/cmd/nusb/ether/smsc.c

This file supports SMSC LAN95XX USB Ethernet controllers. It defines register addresses, burst/flow-control defaults, EEPROM command bits, MAC/RX/TX flags, MII access bits, PHY advertisement/status bits, and receive/transmit framing flags.

Like `lan78xx.c`, it uses 32-bit vendor register helpers and internal-MII helpers. `eepromr()` reads the MAC address bytes from EEPROM. `phyinit()` resets the PHY, advertises 10/100 and pause capabilities, clears pending PHY interrupt state, enables autonegotiation-complete/linkdown interrupt masks, and restarts autonegotiation.

`smscreceive()` reads either burst-sized or max-packet buffers, parses per-packet RX headers, drops error packets, strips the four-byte trailing checksum/status from complete packets, handles multiple aggregated frames, and sends good frames to `etheriq()`. `smsctransmit()` prepends two 32-bit TX headers with first/last segment bits.

Promiscuous and multicast callbacks adjust `Maccr` bits. `smsclinkspeed()` reports link-down, 100 Mbps, or 10 Mbps from PHY status. `smscinit()` resets hardware and PHY, reads or uses the configured MAC, programs address registers, burst behavior, interrupts, LEDs, flow control, VLAN tag, disables checksum offload, clears filters, initializes PHY, enables interrupts/MAC/TX, and installs callbacks.

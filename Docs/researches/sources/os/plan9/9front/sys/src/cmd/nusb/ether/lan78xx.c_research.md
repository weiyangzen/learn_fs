# File Research: sources/os/plan9/9front/sys/src/cmd/nusb/ether/lan78xx.c

This file supports Microchip/SMSC LAN78XX USB Ethernet controllers, including the Ethernet core used in LAN7515 hub-plus-Ethernet devices. It defines LAN78XX register addresses, USB vendor requests, FIFO sizing, burst parameters, EEPROM access bits, RX/TX framing flags, MAC/PHY control bits, and MII advertisement/status constants.

The register helpers `wr()` and `rr()` perform 32-bit vendor control writes/reads. `miird()` and `miiwr()` access the internal PHY through the MII address/data registers. `eepromr()` reads bytes from EEPROM by polling the E2P command register. `phyinit()` resets the PHY, advertises 10/100 plus pause/asymmetric pause and gigabit full-duplex, configures LED modes, and restarts autonegotiation.

The receive path reads a burst-sized buffer, parses LAN78XX RX command headers, drops packets with `Rxerror`, aligns to four-byte packet boundaries, and submits frames to `etheriq()`. Transmit prepends two 32-bit TX command words including frame length and FCS request.

Promiscuous and multicast callbacks update `Rfectl` accept bits. `lan78xxlinkspeed()` derives 0/10/100/1000 Mbps from PHY status and partner ability. `lan78xxinit()` performs hardware and PHY reset, reads or applies the MAC address, programs address filters, USB burst mode, FIFO sizes, interrupts, LEDs, flow control, checksum-offload disable, PHY init, MAC RX/TX enable, FIFO enable, and callback installation.

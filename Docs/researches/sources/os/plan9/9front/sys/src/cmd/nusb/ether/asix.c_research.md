# File Research: sources/os/plan9/9front/sys/src/cmd/nusb/ether/asix.c

This file implements ASIX USB Ethernet chip support for the common nusb Ethernet server. It covers older AX88178/AX88772-style devices and AX88179/AX88178A-style gigabit devices, each with different vendor control requests and packet framing.

The common ASIX section defines media-mode bits, RX-control bits, MII register bits, and helpers for vendor reads/writes, GPIO, PHY id, RX control, MII reads/writes, and EEPROM reads. The AX88178/AX88772 receive path parses ASIX packet headers containing length and one's-complement length, extracts one or more Ethernet frames from a USB transfer, and passes valid frames to `etheriq()`. Transmit prepends the ASIX length/check header and emits a padding header when the transfer is max-packet aligned.

`a88178init()` performs GPIO and EEPROM-dependent reset sequencing, reads the MAC address, configures PHY advertisement including gigabit where appropriate, starts autonegotiation, programs medium mode and RX control, and installs callbacks. `a88772init()` handles embedded/external PHY selection, reset sequencing, MAC read, PHY advertisement, IPG setup, RX enable, and callback installation.

The AX88179 path defines a separate register-access API, receive aggregation parser, transmit header format, link wait, promiscuous/multicast toggles, and link-speed callback. `a88179init()` resets PHY/clock state, handles 88179A firmware compatibility, optionally sets or reads the MAC address, enables RX filtering and power behavior, waits for link, selects bulk-in queue parameters based on USB/link speed, programs medium mode, and installs the callbacks used by `ether.c`.

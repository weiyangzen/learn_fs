# File Research: sources/os/plan9/9front/sys/src/cmd/nusb/ether/url.c

This file supports Realtek RTL8150 USB 10/100 Ethernet adapters. It defines the vendor memory request, control/read/write selectors, device register offsets, command/RX/TX/media bits, PHY/MII fields, EEPROM offsets, and receive-status bits.

The `mem()` helper performs USB vendor memory reads or writes to device register offsets; `csr8r`, `csr16r`, `csr8w`, `csr16w`, and `csr32w` layer typed CSR access on top. `reset()` sets the software-reset bit and polls until it clears.

`urlreceive()` reads a packet plus four-byte trailer, discards short transfers, uses the two-byte receive status at the end to require a valid packet bit, and queues valid frames. `urltransmit()` pads frames shorter than 60 bytes before writing them directly to the bulk endpoint.

Promiscuous and multicast callbacks update RX configuration accept bits (`Aap`, `Aam`). `urlinit()` resets the device, reads the MAC address from ID registers, resets again, writes the MAC back, configures transmit retry/interframe gap and receive filters, clears multicast hash registers, enables TX/RX, and installs callbacks.

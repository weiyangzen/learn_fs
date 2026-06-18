# File Research: sources/os/plan9/9front/sys/src/cmd/nusb/ether/aue.c

This file supports ADMtek Pegasus-style USB Ethernet adapters. It defines vendor register read/write requests, control/status register bits, EEPROM/MII register addresses, GPIO bits, and packet status masks.

The CSR helpers read and write 8- and 16-bit device registers through USB vendor control requests. `eeprom16r()` reads 16-bit EEPROM words by programming the EEPROM address/control registers and polling for completion. `reset()` resets the MAC and toggles GPIOs needed by the chip.

`auereceive()` reads a USB packet, removes the four-byte trailing status/length header, drops packets with error bits or invalid lengths, and queues valid frames through `etheriq()`. `auetransmit()` prepends a two-byte frame length before writing to the OUT endpoint.

Promiscuous and multicast callbacks update receive-control bits (`C2prom` and `C0allmulti`). `aueinit()` resets the chip, reads the MAC address from EEPROM, writes it into PAR registers, disables promiscuous mode, enables RX/TX and endpoint counter clearing, then installs the common Ethernet callbacks.

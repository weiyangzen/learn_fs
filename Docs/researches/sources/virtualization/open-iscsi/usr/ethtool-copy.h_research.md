# File Research: sources/virtualization/open-iscsi/usr/ethtool-copy.h

Vendored copy of Linux ethtool userspace ABI definitions. It defines common ethtool structs, command numbers, link capability bits, speed/duplex/port constants, wake-on-LAN flags, RX flow classification structures, and reset flags.

Notable contents:
- `struct ethtool_cmd` and helpers to set/read 32-bit speed split across `speed` and `speed_hi`.
- Driver info, WOL, EEPROM, coalescing, ring, pause, strings, test, stats, permanent address, RX NFC, flash, and reset structs.
- `ETHTOOL_G*`/`ETHTOOL_S*` command constants up through reset.
- Supported/advertised link mode bit masks up through 10G/backplane-era modes.
- RX hash and classification constants.

This file exists to compile against stable ethtool definitions independent of the host system headers.

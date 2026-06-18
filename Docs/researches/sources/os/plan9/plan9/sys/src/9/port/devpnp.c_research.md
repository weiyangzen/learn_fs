# File Research: sources/os/plan9/plan9/sys/src/9/port/devpnp.c

Implements `#$`, a hardware discovery/control device for ISA PnP and PCI configuration space. Top-level directories are `pnp` and `pci`.

ISA PnP support uses the standard initiation key, isolation protocol, card serial/checksum reading, CSN assignment, and resource-data reads through a configured READ_DATA port. Discovered `Card` records store CSN, ids, optional config string, and raw resource byte count. `pnpreset` can preload expected cards/config strings from kernel configuration and then scan.

The `pnp` directory exposes `ctl`, plus per-card `csnNctl` and `csnNraw`. `ctl` reports enabled/disabled state and accepts `port <addr>` to scan and `debug <n>`. `csnNctl` reports the serial identifier and accepts configuration writes, though `wrconfig` is currently a stub. `csnNraw` reads raw resource data after waking the selected card.

PCI support enumerates `Pcidev` entries under `pci`, exposing `<bus>.<dev>.<fn>ctl` and `<bus>.<dev>.<fn>raw`. `ctl` reports class codes, vendor/device id, interrupt line, and BARs. `raw` reads/writes PCI config space up to 256 bytes, using 32/16/8-bit accesses depending on offset and length alignment.

The device is highly platform-specific and depends on ISA I/O port access, PCI config helpers, and kernel config strings. ISA PnP configuration writing is explicitly unimplemented.

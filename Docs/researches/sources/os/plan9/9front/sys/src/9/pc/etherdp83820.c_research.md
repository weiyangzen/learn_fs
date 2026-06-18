# File Research: sources/os/plan9/9front/sys/src/9/pc/etherdp83820.c

National Semiconductor DP83820 Gigabit Ethernet driver, registered as `DP83820`.

Primary role:
- Drives DP83820 PCI gigabit NICs using memory-mapped registers, descriptor rings, serial EEPROM, MII bit-banging, optional MII bus integration, and interrupt-driven RX/TX.

Key structures:
- `Desc`: ring descriptor with link pointer, buffer pointer, command/status, extended status, block pointer, and padding.
- `Ctlr`: MMIO/PCI state, EEPROM cache, config/imr state, attach/init locks, MII pointer, RX buffer pool, RX/TX rings and indices, cached RX/TX config, MIB counters, and transmit error counters.

Important behavior:
- `dp83820pci()` scans PCI Ethernet devices, accepts NatSemi DP83820 ID `0x100B:0x0022`, maps BAR1 MMIO, resets the controller, enables bus mastering, and links controllers.
- `dp83820pnp()` claims a controller, sets generic `Ether` fields, derives MAC from EEPROM if not overridden, installs callbacks, and enables interrupts.
- `dp83820attach()` creates an MII bus unless TBI is enabled, discovers PHYs, allocates descriptor memory, and calls `dp83820init()`.
- `dp83820init()` halts old state, grows RX buffer pool, initializes RX descriptor ring and receive filter address, initializes TX descriptor ring, configures RX/TX thresholds, applies duplex/speed config, clears MIBs, programs interrupt holdoff, enables interrupts, and starts RX/TX.
- `dp83820transmit()` cleans completed TX descriptors, accounts TX errors, frees blocks, queues new output blocks, and kicks TX.
- `dp83820interrupt()` handles RX completions, RX idle restart, TX underrun threshold increase, TX completion, MIB accumulation, PHY interrupts, and unknown interrupt reporting.
- `dp83820ifstat()` reports MIB counters, RX idle count, TX error counters, EEPROM words, and current PHY registers.
- `dp83820halt()` disables interrupts/RX/TX, freezes MIBs, and frees RX/TX blocks.
- `dp83820detach()` soft-resets the device; shutdown wraps it.

EEPROM/MII:
- `atc93c46r()` bit-bangs ATC93C46-compatible serial EEPROM and discovers EEPROM address size.
- `dp83820miimir()`/`dp83820miimiw()` bit-bang IEEE MII frames through `Mear`.

Research notes:
- Promiscuous is stubbed and multicast is no-op because initialization accepts all multicast (`Aam`) and broadcast/perfect match.
- The file has apparent defects worth rechecking before relying on it: `dp83820rballoc()` assigns `desc->bp` but then uses `bp->rp` while `bp` can still be nil, and `dp83820ifstat()` indexes `ctlr->mibd` using register-offset-derived expressions rather than small counter indices.
- The driver explicitly assumes little-endian and 32-bit host operation.

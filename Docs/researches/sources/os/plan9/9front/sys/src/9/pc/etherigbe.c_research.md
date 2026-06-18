# File Research: sources/os/plan9/9front/sys/src/9/pc/etherigbe.c

Implements the Plan 9 Intel PRO/1000-era gigabit Ethernet driver for 82543/82544/82540/82541/82545/82546/82547-class devices.

Key behavior:
- Defines PCI IDs, MAC registers, EEPROM/flash bits, MDI access, flow control, RX/TX descriptor formats, interrupts, statistics, and chip-specific flags.
- Probes Intel gigabit Ethernet PCI devices, maps MMIO BAR0, resets the device, reads EEPROM/SPI contents, validates checksum `0xBABA`, and programs receive address slots.
- Handles 82543GC specially with GPIO-bitbanged MDIO; later chips use the MDIC register.
- Initializes PHY/MII, flow control, collision distance, speed/duplex, and autonegotiation-related settings.
- Allocates aligned RX/TX descriptor memory plus per-descriptor block arrays during attach.
- RX kproc initializes descriptors, enables RX, sleeps on RX interrupts, consumes descriptor-done packets, applies checksum flags when valid, and replenishes buffers.
- TX path frees completed descriptors, fills the TX ring from `edev->oq`, requests TX descriptor writeback when the ring is near full, and re-enables TX interrupts as needed.
- Interrupt handler masks active causes, wakes link/RX workers, directly calls transmit cleanup on TX writeback, and restores interrupt masks.
- Provides `ifstat` with hardware statistics, EEPROM dump, PHY register dump, and driver counters.
- Provides ctl command `rdtr` to tune receive delay timer.

Dependencies:
- Uses Plan 9 PCI, Ethernet, MII, block, interrupt, and command parsing APIs.
- Encodes Intel EEPROM Microwire/SPI transactions through `Eecd` bit operations.

Research notes:
- Header comments say this CAT5 path does not integrate fiber support and checksum offload is intentionally incomplete.
- RX checksum offload programming is disabled in `igberxinit` because of known hardware/driver bugs.
- Multicast filter bits are never cleared because multiple multicast addresses can hash to the same bit.

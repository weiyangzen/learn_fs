# File Research: sources/os/plan9/9front/sys/src/9/pc/etheri225.c

Implements a Plan 9 PCI Ethernet driver for Intel i225/i226 2.5GbE controllers.

Key behavior:
- Defines Intel i225/i226 register offsets, interrupt bits, EEPROM/MDI/semaphore controls, RX/TX descriptor formats, and statistic registers.
- Discovers supported Intel PCI IDs, maps BAR0 MMIO, enables PCI bus mastering, and registers as `i225`.
- Resets the MAC, waits for EEPROM autoload, marks the driver active, disables EEE, initializes the MAC address and multicast table.
- Uses hardware semaphores and sync bits to serialize PHY/EEPROM/MDI access, then attaches a Plan 9 `Mii` bus with clause 22/45 autonegotiation.
- Allocates one 1024-entry TX ring and one 1024-entry RX ring, both with 16-byte descriptors.
- Runs separate kprocs for TX completion/fill, RX completion/refill, link status, and periodic statistics accumulation.
- Interrupt handler masks/restores interrupts, wakes link/RX/TX worker rendezvous points for link, queue 0 RX, and queue 0 TX events.
- RX path concatenates multi-descriptor packets, drops errored chains, marks checksum flags, and passes packets to `etheriq`.
- TX path dequeues from `edev->oq`, writes DMA descriptors, requests status, and frees completed blocks.
- Exposes `ifstat`, promiscuous mode, multicast hash insertion, shutdown reset, and `Ether` callbacks.

Dependencies:
- Uses Plan 9 kernel Ethernet, PCI, MII, DMA, block pool, rendezvous, and kproc APIs.
- Depends on i225/i226 MMIO register semantics and PCI write-address translation through `PCIWADDR`.

Research notes:
- Multicast removal is not implemented; `i225multicast` only sets hash bits.
- Only queue 0 is actively used even though interrupt vector setup covers four queue pairs.
- Potential controller-list issue: `i225pci` assigns `i225ctlr->link = c` rather than linking through `i225ctlrtail`, which can lose controllers after the second device.

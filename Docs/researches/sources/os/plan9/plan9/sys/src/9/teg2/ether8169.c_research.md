# File Research: sources/os/plan9/plan9/sys/src/9/teg2/ether8169.c

Realtek RTL8110/8168/8169-family gigabit Ethernet driver adapted for Tegra/TrimSlice PCIe, with explicit cache maintenance for DMA.

Key responsibilities:
- Scans PCI Ethernet devices for supported Realtek/Corega IDs, maps BAR2 MMIO directly, wakes devices from PCI power management, validates hardware MAC version, resets the device, initializes MII, and enables bus mastering.
- Registers as `rtl8169` through `ether8169link`.
- Provides Ethernet callbacks for attach, transmit, interrupt, ifstat, promiscuous, multicast, and shutdown.
- Manages 1024-entry TX and RX descriptor rings, a 4096-block private receive pool, and a hardware tally-counter DMA block.
- Initializes receive/transmit configuration, C+ command bits, descriptor base addresses, receive maximum size, multicast hash registers, interrupt mask, and chip-version-specific magic settings.
- Runs receive and transmit kernel processes woken by interrupt status bits.
- Handles link state through `Phystatus` and MII auto-negotiation helpers.
- Maintains hardware/software statistics and exposes PHY register dumps through `ifstat`.
- Handles restart after RX FIFO overflow, descriptor unavailable, receive errors, and selected controller stalls.

Important behavior:
- Uses `allcache->wbse` before TX DMA and `allcache->invse` after RX DMA.
- RX accepts only single-descriptor packets with `Fs|Ls` and no receive error summary; CRC is stripped by subtracting four bytes.
- Multicast hashes are accumulated and never cleared on removal; PCIe variants reverse hash-register byte order.
- Attach sets `l1ptstable.word` after RTL8169 initialization so secondary CPUs can safely copy CPU0's L1 page table.
- `rtl8169interrupt` masks RX/TX causes while waking worker processes, then workers re-enable the masks.

Dependencies and assumptions:
- Depends on Plan 9 PCI helpers, `devether`, `ethermii`, cache vtables, kernel processes, and Tegra PCIe interrupt completion (`pcieintrdone`).
- Assumes 32-bit DMA addresses by writing high descriptor address words as zero.
- Assumes Realtek PHY address 1 and TrimSlice IRQ routing through `Pcieirq`.
- Does not `vmap` the MMIO BAR because the TrimSlice mapping is already usable.

Notable risks:
- Several chip setup paths use undocumented or vendor-driver-derived magic values.
- Restart is a large hammer: it drains rings briefly, resets hardware, frees RX buffers, reinitializes, and wakes workers.
- `rtl8169attach` calls `miistatus(ctlr->mii)` even if MII setup failed, relying on helper nil checks.
- RX fragmentation/oversize behavior drops or panics on unexpected descriptor lengths.

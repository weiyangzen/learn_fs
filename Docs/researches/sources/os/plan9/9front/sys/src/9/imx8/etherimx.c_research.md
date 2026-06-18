# File Research: sources/os/plan9/9front/sys/src/9/imx8/etherimx.c

Role: i.MX8 ENET Ethernet MAC driver with RGMII PHY/MII support and descriptor-ring DMA.

Key responsibilities:
- Defines ENET register layout, interrupt bits, MAC controls, MII management, FIFO, coalescing, and descriptor status bits.
- Uses uncached descriptor rings and a block pool for 256 RX and 256 TX descriptors.
- Implements MDIO read/write using ENET MMFR and MII interrupt/completion rendezvous.
- Interrupt handler wakes RX, TX, MII I/O, and link waiters and clears event bits.
- Resets/shuts down MAC via `ECR_RESET`, masks/clears events, and initializes RGMII/max frame settings.
- `attach()` probes PHY, sets MAC address/filter tables, allocates/replenishes RX buffers, initializes TX descriptors, enables coalescing, and starts RX/TX/free/link kernel processes.
- `txproc()` dequeues outgoing blocks, maps them to descriptors, cleans cache, and activates TX DMA.
- `frproc()` reclaims completed TX descriptors and frees blocks.
- `rxproc()` receives complete non-error frames, invalidates cache, strips FCS, delivers to `etheriq`, and replenishes descriptors.
- `linkproc()` negotiates PHY, updates ENET speed/duplex/flow-control bits, and updates Plan 9 link state.
- `pnp()` sets pad muxing, clock rates/gates, MAC address from OCOTP fuses, and interrupt registrations.

Dependencies:
- Uses Plan 9 `etherif`, `ethermii`, `netif`, block pool, kernel process, and cache DMA helpers.
- Depends on `iomuxpad`, `setclkrate`, `setclkgate`, `dmaflush`, and GIC interrupts.

Notes and risks:
- Descriptor memory comes from `ucalloc()` to avoid cache-coherency issues.
- Multicast hash is rebuilt from `edev->maddr`.
- RX replenish waits indefinitely through `resrcwait()` if buffer allocation fails.

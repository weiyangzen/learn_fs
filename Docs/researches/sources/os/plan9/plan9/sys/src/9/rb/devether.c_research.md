# File Research: sources/os/plan9/plan9/sys/src/9/rb/devether.c

Atheros AR71xx Ethernet driver and Plan 9 `#l` Ethernet device for RouterBOARD RB450G.

Key responsibilities:
- Defines ARGE MAC/DMA register layout, descriptor format, controller state, and two fixed interface descriptors.
- Manages generic Ethernet netif plumbing: probing, attach, walk/open/read/write/stat, loopback, output queue, and shutdown.
- Initializes RX/TX DMA descriptor rings and a shared receive-block pool.
- Handles RX/TX interrupts by waking receive/transmit kprocs.
- RX kproc drains descriptors, strips CRC, and passes packets through `etheriq`.
- TX kproc reclaims descriptors, copies queued blocks to hardware descriptors, kicks DMA, and handles underruns.
- Provides MII/switch scaffolding, though AR8316 switch support is under `NOTYET` and normal `athmii` is stubbed.
- Implements multicast/promiscuous stubs and interface statistics.

Important behavior:
- Leaves much of ARGE0 as RouterBOOT initialized; copies or configures only key registers.
- Only all-relevant DMA interrupts are enabled; TX interrupts are mostly used for ring pressure/underrun.
- Uses uncached `KSEG1` descriptor memory and explicit `dcflush`/`coherence` around DMA buffers.
- Computes input/output queue sizes from link Mbps with sanity caps.
- Uses global `arge0mac`/`arge1mac` from RouterBOARD config.

Dependencies:
- Depends on Plan 9 `netif`, AR7161 interrupt levels, MII helper headers, block allocator, cache helpers, and `io.h`.

Notable risks:
- File TODO notes promiscuous mode and ether1/switch/MII initialization are incomplete.
- MII initialization is stubbed, so link setup relies on firmware or fixed config.
- Shared RX block pool is global across controllers.
- Direct DMA descriptor ownership requires strict cache coherency discipline.

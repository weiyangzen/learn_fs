# File Research: sources/os/plan9/9front/sys/src/9/mt7688/ether7688.c

MT7688 MediaTek Ethernet/PDMA driver with integrated switch/PHY setup. It defines RX/TX descriptor formats, PDMA global config, interrupt masks, switch MII access, controller state, and Plan 9 `Ether` callbacks.

The driver reads/writes system, Ethernet, and switch registers through fixed MMIO macros. MII access goes through switch PCTL registers. `doreset` and `ethreset` apply switch and PHY reset/init sequences with many hard-coded register values. `getmacaddr` reads GDMA1 MAC registers.

`attach` initializes switch/PHY/MII, allocates uncached descriptor rings in KSEG1, allocates RX blocks, initializes TX descriptors, programs PDMA ring pointers/counts/indexes, enables RX/TX interrupts and DMA, sets VLAN ethertype, marks link up, and starts `rxproc`/`txproc`.

`rxproc` waits for RX descriptors marked done, flushes cache, passes blocks to `etheriq`, replenishes buffers, and advances CPU index. `txproc` reads outbound queue blocks, waits for free TX descriptors, pads short frames, flushes cache, and advances TX index. `etherinterrupt` wakes RX/TX processes and records DMA/spurious stats.

Notable risks: many switch/PHY constants are magic; TX/RX cache flushing and descriptor ownership are delicate; promiscuous/multicast/shutdown are stubs; link is forced up.

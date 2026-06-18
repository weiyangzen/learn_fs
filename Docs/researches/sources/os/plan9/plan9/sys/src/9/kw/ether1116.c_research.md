# File Research: sources/os/plan9/plan9/sys/src/9/kw/ether1116.c

## Purpose
Implements the Marvell Kirkwood gigabit Ethernet controller and Marvell 88E1116/88E1121-family PHY driver used on SheevaPlug/OpenRD/GuruPlug-like systems.

## Main Data Structures
- `Rx` / `Tx`: hardware DMA descriptors for receive and transmit rings.
- `Mibstats`: memory-mapped MAC statistic counters.
- `Gbereg`: complete register map for the Kirkwood GbE controller, including SMI/MDIO, DMA windows, port config/status, interrupts, queue pointers, MIB counters, and address filters.
- `Ctlr`: software controller state, including descriptor rings, block arrays, ring indices, MII state, port number, receive rendezvous, and accumulated stats.
- `freeblocks`: global pool of aligned receive blocks recycled through a custom `Block.free` hook.

## Receive Path
- `ctlralloc` allocates aligned receive buffers, uncached Rx descriptors, and uncached Tx descriptors.
- `rxreplenish` fills empty Rx descriptors with recycled blocks and hands them to DMA.
- `rxkick` starts/restarts receive queue 0.
- `interrupt` notices receive events, sets `haveinput`, and wakes `rcvproc`.
- `rcvproc` periodically harvests MIB stats and calls `receive`.
- `receive` scans completed Rx descriptors, validates first/last and MAC error bits, invalidates caches for received data, skips the two-byte hardware alignment pad, passes packets to `etheriq`, and replenishes descriptors.

## Transmit Path
- `etheroq` in `devether.c` queues packets to `ether->oq`; this driver’s `transmit` drains that queue.
- `txreplenish` reclaims completed Tx descriptors and frees transmitted blocks.
- `transmit` writes back packet cache lines, fills Tx descriptors, marks them DMA-owned, kicks queue 0, and enables Tx-empty/error interrupts.
- `txkick` starts/restarts transmit queue 0.

## Interrupt and Link Handling
- `interrupt` clears main and extended interrupt causes, handles receive, transmit-end, PHY status changes, Tx/Rx errors, overrun/underrun, link-change completion, and unknown causes.
- `ethercheck` warns when the main interface has not sent or received packets for `Etherstuck` seconds.
- `etheractive` updates last-activity time.

## PHY/MII Handling
- `miird` and `miiwr` implement MDIO/SMI access through controller registers with busy/read-valid waits.
- `mymii` probes PHYs, with special handling for dual-port boards whose second Ethernet controller shares PHY discovery through controller 0.
- `kirkwoodmii` allocates `Mii`, probes PHYs, resets/autonegotiates if needed, waits for autonegotiation, and updates `ether->mbps`.
- `miiphyinit` configures Marvell PHY LED behavior, RGMII power, RGMII timing delay, MDIX, and exits power-down/energy-detect modes.

## Hardware Initialization
- `reset` allocates `Ctlr`, assigns IRQ and register base from `soc.ether`, sets I/O voltage config, shuts down/reset hardware, sets RGMII mode, assigns PHY address, initializes MII/PHY, reads/configures MAC address filters, and installs Ethernet callbacks.
- `ctlrinit`, called on first attach, configures DRAM access windows, descriptor rings, MIB counters, SDMA burst/coalescing, interrupt masks, address filters, port config, RGMII/port serial control, MTU bucket, receive kproc, and receive queue start.
- `shutdown` quiesces queues, resets the controller, powers down port serial control, and clears descriptor pointers.
- `cfgdramacc` configures controller DRAM windows for DMA.

## Control and Stats
- Custom control command `jumbo on|off` exists, but `jumbo on` immediately errors as disabled because the input queue does not expect jumbo frames.
- `ifstat` reads and accumulates hardware MIB counters, reports interrupt/error/ring/link/flow/stat counters, and accounts for errata around high halves of byte counters.
- `archetheraddr` reads MAC address registers, synthesizes a secondary MAC if needed, and programs unicast/multicast filters.
- `ether1116link` registers this driver as card type `88e1116`.

## Dependencies and Integration
Integrates with the generic `devether.c` layer, `ethermii.c` MII helpers, Kirkwood `soc` registers, cache/L2 cache maintenance routines, interrupt controller, Plan 9 queues/blocks, and IP/Ethernet packet definitions.

## Risks and Notes
DMA correctness depends on uncached descriptors, explicit cache writeback/invalidate for packet buffers, alignment, and coherent register writes. The dual-PHY board support is acknowledged as a hardware-specific hack. Receive buffering is shared globally, and low buffer conditions produce kernel diagnostics.

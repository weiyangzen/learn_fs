# File Research: sources/os/plan9/plan9/sys/src/9/ppc/etherfcc.c

## Role

Hardware Ethernet driver for MPC8260 FCC Ethernet controllers, registered as Ethernet card type `"fcc"`.

## Main Data

Defines FCC Ethernet buffer descriptor bits, FCC mode/event bits, `Etherparam` matching parameter RAM, and `Ctlr` holding FCC identity, port, MII GPIO pins, ring state, receive buffers, PHY state, timer, and hardware statistics. Uses 128 RX and 128 TX descriptors with cache-line-aligned receive buffers.

## Control Flow

`reset` validates CPU speed and port, allocates controller state and descriptor rings, allocates RX buffers, runs `fccsetup`, and wires Ethernet callbacks. `fccsetup` configures board port pins and clock routing for FCC1-3, initializes parameter RAM, sets station address, clears events, enables FCC events, issues `InitRxTx`, allocates/probes MII, and starts autonegotiation.

`attach` enables RX/TX and starts a periodic link timer. `transmit` calls `txstart`, which dequeues outbound blocks into TX descriptors and hands them to hardware. `interrupt` handles RX frames, RX errors, TX completions/errors, descriptor freeing, restart-on-error, and stats. `ifstat` prints driver and PHY state. MII read/write is bit-banged over configured port pins. `fccltimer` updates link speed and duplex from PHY status.

## Dependencies

Depends on `imm.h`, `blast.h` pin masks, descriptor-ring helper `ioringinit`, CPM command `cpmop`, cache flush/zap functions, `etherif.h`, and `ethermii`.

## Risks

Descriptor/data cache coherence is critical. TX path panics on unexpected descriptor or alignment state. Multicast filtering falls back to promiscuous behavior. MII bit-banging uses fixed delays and assumes MDIO pins on port 3 in read/write helpers, despite setup differences.

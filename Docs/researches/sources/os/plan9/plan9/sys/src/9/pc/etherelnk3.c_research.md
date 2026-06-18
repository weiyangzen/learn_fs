# File Research: sources/os/plan9/plan9/sys/src/9/pc/etherelnk3.c

## Purpose

This file is the Plan 9 PC ethernet driver for 3Com EtherLink III, Fast EtherLink, and Fast EtherLink XL adapters. It supports ISA, EISA, PCI, PCMCIA, and CardBus-era devices, including 3C509, 3C579, 3C589/3C562, 3C59x Vortex, 3C90x Boomerang/Cyclone/Tornado-class boards, and related OEM variants.

The driver owns hardware discovery, EEPROM access, media selection, reset/setup, PIO and bus-master transmit/receive paths, interrupt handling, per-device statistics, and registration with the generic Plan 9 ethernet layer under `elnk3`, `3C509`, and `3C575`.

## Public Entry Points

- `etherelnk3link()` registers card names with `addethercard`.
- `etherelnk3reset()` is the generic ethernet reset/probe hook. It scans controllers once, binds an unused controller to an `Ether`, reads EEPROM identity and station address, selects media, allocates receive/transmit resources, configures thresholds, and installs callbacks.

Installed `Ether` callbacks:

- `attach()` enables RX/TX, interrupt masks, packet filters, CardBus interrupt acknowledgment, and receive DMA/list priming.
- `transmit()` starts either FIFO/PIO transmit or 3C90x descriptor-based download transmit.
- `interrupt()` handles adapter interrupts and dispatches RX/TX/statistics/error work.
- `ifstat()` formats driver and hardware statistics.
- `promiscuous()` and `multicast()` update receive filters.
- `shutdown()` resets the controller on shutdown.

## Hardware Model

The file defines the 3Com register-window architecture and command/status protocol:

- Common command/status registers at offsets `CommandR`/`IntStatusR`.
- Command opcodes for reset, RX/TX enable/disable, DMA start, interrupt enable/acknowledge, statistics, power, stall/unstall, thresholds, and filters.
- Window 0 setup/EEPROM registers.
- Window 1 operating FIFO/RX/TX status registers.
- Window 2 station address registers.
- Window 3 FIFO/internal config/media options registers.
- Window 4 diagnostics, media status, and bit-banged MII management.
- Window 5 interrupt/filter/threshold state.
- Window 6 statistics.
- Window 7 simple bus-master registers.
- 3C90x extended registers for upload/download descriptor rings.

`Ctlr` stores the selected I/O port, PCI/CardBus metadata, interrupt line, active/attached flags, current media, EEPROM command variant, receive-status format, bus-master mode, locks, current receive buffer, FIFO transmit state, 3C90x upload/download descriptor rings, interrupt/stat counters, queue high-water marks, and CardBus function-memory mapping.

## Discovery Paths

The driver supports multiple bus families:

- `tcm59Xpci()` scans PCI vendor `0x10B7` ethernet-class devices, requires I/O BAR access, allocates I/O space, resets TX/RX, acknowledges stale interrupts, records CardBus-specific EEPROM and function-memory details for device IDs `0x5157` and `0x6056`, and enables PCI bus mastering with `pcisetbme`.
- `tcm5XXeisa()` checks for an EISA machine signature, walks EISA slots, validates 3Com manufacturer/product IDs, enables matching boards, resets them, reads IRQ resources, and records controllers.
- `tcm509isa()` uses the 3Com ISA ID-port activation sequence. `idseq()` emits the magic LFSR identification sequence; `activate()` reads manufacturer/address configuration serially from `IDport`; matching adapters are tagged and activated unless in EISA mode.
- `tcm5XXpcmcia()` accepts caller-supplied PCMCIA types `3C589`, `3C562`, and `589E`.

Controllers are appended to the global `ctlrhead`/`ctlrtail` list by `tcmadapter()`. `etherelnk3reset()` claims the first inactive controller matching the requested `ether->port`, or any inactive controller when no port is specified.

## Reset And Initialization Flow

`etherelnk3reset()`:

1. Performs one-time PCI/EISA/ISA scans.
2. Claims a controller or creates one for a matching PCMCIA card.
3. Fills `ether->ctlr`, `port`, `irq`, and `tbdf`.
4. Reads EEPROM device ID at offset `0x03`.
5. Selects mode:
   - `busmaster = 2` for PCI 3C90x-style descriptor upload/download devices.
   - `busmaster = 1` for 3C59x/Vortex simple bus-master receive devices.
   - `busmaster = 0` for older PIO devices and non-PCI fallback.
6. Reads or preserves the station address, then writes it into window 2.
7. Honors `media=` options and chooses transceiver/media through EEPROM/config bits or autoselection.
8. Configures MII, 100BaseTX/FX, 10BaseT, or 10Base2-specific media status and duplex settings.
9. Clears TX status and statistics.
10. Allocates either a single receive buffer or 3C90x upload/download descriptor rings.
11. Sets TX start and RX early thresholds.
12. Installs generic ethernet callbacks.

`resetctlr()` has extra handling for 905B/CardBus-style devices, including LED/reset-option tweaks for IDs `0x5157` and `0x6056`.

## Media And PHY Handling

The `media[]` table maps option strings to hardware transceiver encodings:

- `10BaseT`
- `10Base2`
- `100BaseTX`
- `100BaseFX`
- `aui`
- `mii`

`autoselect()` probes advertised media, prefers MII when present, otherwise tries 100BaseTX then 10BaseT by programming the transceiver and checking link beat. `setxcvr()` writes either old 3C5x9 address-config bits or newer internal-config transceiver bits. `setfullduplex()` enables full duplex in `MacControl`.

MII access is implemented by bit-banging `PhysicalMgmt`:

- `miimdo()` writes management bits.
- `miimdi()` reads management bits.
- `miir()` performs a full MII read transaction.
- `scanphy()` walks PHY addresses and returns the first plausible PHY, falling back to address 24.

MII negotiation results are used to set `ether->mbps` and full-duplex mode. Options such as `fullduplex`, `100BASE-TXFD`, and `force100` override advertised mode bits.

## Transmit Path

The driver has two transmit implementations:

- `txstart()` handles FIFO/PIO transmission. It drains `ether->oq`, checks `TxFree`, writes packet length and padded packet data to `Fifo`, and arms a `txAvailable` interrupt when FIFO space is insufficient.
- `txstart905()` handles 3C90x download descriptors. It frees completed descriptors by comparing against `DnListPtr`, fills descriptor entries from `ether->oq`, stalls/un-stalls the download engine when appending to a live list, updates queue high-water counters, and starts the download engine if idle.

`transmit()` serializes through `ctlr->wlock` and chooses descriptor or FIFO mode based on `ctlr->dnenabled`.

TX completion and errors are processed in `interrupt()`. Underrun raises the TX threshold; jabber, underrun, and max-collision conditions trigger TX reset and re-enable. Descriptor mode forces a download completion pass after reset.

## Receive Path

The file supports three receive models:

- PIO receive via `receive()`, reading packet data from `Fifo`.
- Simple bus-master upload via `startdma()` and `receive()`, using a single receive buffer and window 7 master registers.
- 3C90x descriptor upload via `receive905()`, walking upload descriptors completed by hardware.

`rbpalloc()` allocates receive blocks with 32-byte alignment for EISA bus mastering. `init905()` allocates and 8-byte-aligns upload and download descriptor arrays, creates receive blocks for upload descriptors, links upload descriptors in a ring, and initializes download-ring bookkeeping.

`receive()` loops while `RxStatus` says a packet is complete, accounts for old-style embedded RX errors or newer `RxError` values, discards errored or unallocatable packets, reads or finalizes data, restarts simple DMA when needed, delivers successful packets with `etheriq`, and rotates the receive buffer.

`receive905()` walks completed upload descriptors, tallies upload error bits, delivers good blocks, replaces delivered buffers, clears descriptor status, un-stalls upload, and tracks receive batching statistics.

## Interrupt Handling

`interrupt()`:

- Validates interrupt status and counts bogus interrupts.
- Saves/restores the current register window.
- Reads timer counters for profiling.
- Handles `hostError` by reading FIFO diagnostics, treating all-ones status/diagnostic on ejectable CardBus IDs as probable ejection, resetting TX or RX paths depending on diagnostic bits, and printing diagnostics.
- Dispatches receive work for `transferInt` and `rxComplete`.
- Acknowledges and handles 3C90x upload completion.
- Processes TX completion stack and TX errors.
- Handles FIFO `txAvailable` and descriptor `dnComplete`.
- Refreshes hardware statistics on `updateStats`.
- Acknowledges currently unused `rxEarly`.
- Panics on unhandled interrupt-mask bits.
- Acknowledges the interrupt latch and CardBus function interrupt when applicable.

The handler uses `ctlr->wlock` to serialize register-window changes and shared TX/RX state.

## Statistics And Control Surface

`statistics()` snapshots window-6 counters into `ctlr->stats`, including upper bits for frame counts and `BadSSD` for MII/100Base media. `ifstat()` forces a statistics refresh and emits:

- interrupt and bogus-interrupt counts
- timer totals
- hardware counters such as collisions, overruns, good frames, bytes received/transmitted
- upload/download queue and interrupt counters when descriptor paths are enabled
- bad SSD count

Receive filter control is intentionally simple. `promiscuous()` and `multicast()` recompute `SetRxFilter` from broadcast, individual, multicast-present, and promiscuous flags. Multicast does not program a hardware address table; it toggles the aggregate multicast receive bit when `ether->nmaddr` is nonzero.

## Dependencies

This driver depends on Plan 9 PC kernel facilities and ethernet abstractions:

- `u.h`, `lib.h`, `mem.h`, `dat.h`, `fns.h`, `io.h`, `error.h`, `netif.h`, `etherif.h`
- Port I/O helpers: `inb`, `ins`, `inl`, `outb`, `outs`, `outl`, `insl`, `outsl`
- PCI helpers: `pcimatch`, `pcisetbme`, `Pcidev`, BAR metadata
- I/O allocation: `ioalloc`, `iofree`
- Memory mapping: `vmap`
- Kernel allocation/block APIs: `malloc`, `free`, `iallocb`, `freeb`, `Block`
- Queue and network delivery: `qget`, `etheriq`
- Timing and ordering: `delay`, `microdelay`, `coherence`
- Generic ethernet registration: `addethercard`

## Review Notes

- The file is hardware-protocol dense. Register-window selection is protected with `wlock` in operational paths, but helper routines assume callers have selected or restored windows correctly.
- The `rxUnderrun` recovery path in `interrupt()` assigns `s = (port+RxFilter) & 0x000F` after selecting window 5. This looks like it intended to preserve the RX filter value but does not read `RxFilter`; review before relying on RX-underrun recovery.
- `shutdown()` prints unconditionally and then resets the controller, which can be noisy during normal halt/reboot.
- `init905()` panics if receive-ring block allocation fails after allocating descriptor memory. That matches kernel-driver expectations but means reset is not graceful under memory pressure.
- CardBus function memory from `vmap` is stored in `ctlr->cbfn`; no unmap path is present in this file.
- Error recovery comments acknowledge uncertainty around active TX reset, bus-master RX restart, and robustness for underrun/host-error cases.
- Autoselection is explicitly described as a limited heuristic. Media-sensitive changes should be validated on representative old 3Com adapters rather than by static review alone.

## Research Guidance

When changing this file, preserve the distinction among PIO, simple bus-master, and 3C90x descriptor paths. Most logic is keyed by `ctlr->busmaster`, `ctlr->upenabled`, `ctlr->dnenabled`, and `ctlr->rxstatus9`; mixing those paths can break older ISA/EISA devices while appearing correct on PCI devices. Changes to reset, interrupt handling, or media selection should be checked against 3C509/3C589-style old register semantics and 3C90x extended descriptor semantics separately.

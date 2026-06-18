# File Research: sources/os/plan9/plan9/sys/src/9/pc/etherga620.c

## Purpose

This file is the Plan 9 PC ethernet driver for Netgear GA620/GA620T and compatible Alteon Tigon 2 gigabit ethernet adapters, including Alteon AceNIC, DEC DEGPA-SA, and SGI AceNIC variants. It handles PCI discovery, memory-mapped register access, adapter reset, serial EEPROM MAC reads, embedded firmware upload, host/NIC ring setup, transmit/receive processing, firmware event handling, runtime tuning controls, and generic `Ether` registration as `GA620`.

The driver includes `etherga620fw.h`, which supplies the Tigon 2 firmware sections and load/start addresses used during reset.

## Public Entry Points

- `etherga620link()` registers `GA620` through `addethercard`.
- `ga620pnp()` is the reset/probe hook registered with the ethernet layer. It discovers PCI controllers if needed, binds an inactive controller, fills `Ether` identity fields, applies EEPROM or overridden MAC address, initializes runtime structures, and installs callbacks.

Installed `Ether` callbacks:

- `ga620attach()` currently has no extra attach-time work.
- `ga620transmit()` drains queued outbound packets into the send ring.
- `ga620interrupt()` services receive, transmit-completion, event, and replenishment work.
- `ga620ifstat()` reports firmware statistics and driver tunables.
- `ga620ctl()` accepts text commands to tune checksum/coalescing behavior.
- `ga620promiscuous()` and `ga620multicast()` issue firmware commands for receive mode.
- `ga620shutdown()` detaches/resets the adapter.

## Hardware And Firmware Interface

The driver models a firmware-driven NIC interface rather than programming packet movement entirely through raw MAC registers. It defines:

- Memory-mapped CSRs such as `Mhc`, `Mlc`, `Ps`, CPU state/PC registers, mailbox producer/consumer registers, MAC/link registers, DMA configuration, coalescing registers, command ring window, and local-memory window.
- Tigon 2 control bits for endian mode, hard reset, interrupt state, EEPROM bit-banging, SRAM size, PCI command behavior, CPU halt/state, operating mode, local-memory window, and link negotiation.
- Descriptor and control structures shared with firmware:
  - `Host64`
  - event ring element `Ere`
  - command word `Cmd`
  - receive buffer descriptor `Rbd`
  - send buffer descriptor `Sbd`
  - ring control block `Rcb`
  - general information block `Gib`

`Ctlr` stores PCI identity, BAR mapping, EEPROM MAC address, the NIC register pointer, GIB pointer, event/send/receive rings, block side tables, ring indexes mirrored from firmware, interrupt/timing counters, and runtime coalescing/checksum tunables.

Register access goes through:

- `csr32r(ctlr, reg)`
- `csr32w(ctlr, reg, value)`

The implementation assumes the mapped BAR can be treated as an array of 32-bit CSRs.

## PCI Discovery And Reset

`ga620pci()` scans PCI ethernet-class devices and accepts specific vendor/device IDs:

- Netgear GA620 fiber: `vid 0x1385`, `did 0x620A`
- Netgear GA620T copper: `vid 0x1385`, `did 0x630A`
- Alteon AceNIC fiber / DEC DEGPA-SA: `vid 0x12AE`, `did 0x0001`
- Alteon AceNIC copper: `vid 0x12AE`, `did 0x0002`
- SGI AceNIC: `vid 0x10A9`, `did 0x0009`

For a match, it maps BAR0 with `vmap`, allocates a `Ctlr`, records the physical BAR and PCI device, stores the CSR base in `ctlr->nic`, calls `ga620reset()`, and appends successful controllers to the global controller list.

`ga620detach()` performs a hard reset while accounting for unknown endian state by writing reset bits in both byte orders, enables little-endian mode and clear-interrupt behavior, waits for CPU A to halt after EEPROM/flash load, then halts CPU A and CPU B.

`ga620reset()`:

1. Calls `ga620detach()`.
2. Configures SRAM as 512KB banks and synchronous SRAM timing.
3. Initializes PCI state, including read/write command behavior and optional write-and-invalidate cache-line sizing.
4. Sets operating mode to fatal-error reporting, no jumbo fragmentation, byte-swapped DMA data, and word-swapped buffer descriptors.
5. Reads the station address byte-by-byte from AT24C32 serial EEPROM offsets `0x8E` through `0x93`.
6. Uploads firmware text, rodata, data, and zeroed sbss/bss sections into NIC local memory using `ga620lmw()`.

## EEPROM And Local Memory Access

`at24c32io()` is a compact interpreter for serial EEPROM bit operations using `Mlc` bits:

- `C`/`c` clock high/low
- `D` output next data bit
- `E`/`e` enable/disable output
- `I` sample input
- `O`/`o` data high/low
- `:`/`;` define an 8-bit loop

`at24c32r()` performs a random byte read from the AT24C32 EEPROM by issuing start, dummy write of device and address bytes, repeated start, read command, byte read, and stop.

`ga620lmw()` writes or clears NIC local memory through the `Wba`/`Lmw` aperture. It handles window-boundary splitting, uses 32-bit stores, and is used for all firmware sections.

## Runtime Initialization

`ga620init()` configures the runtime host/firmware interface:

- Writes the MAC address to `Mac`.
- Allocates the general information block (`Gib`).
- Allocates the event ring in host memory and points firmware at event producer indexes.
- Clears and initializes the command ring in NIC communications memory.
- Allocates the send ring in host memory, enables optional checksum/coalescing flags, records send consumer indexes, and allocates a parallel `Block*` array for send buffers.
- Allocates the receive standard ring and enables optional receive checksum flags.
- Disables jumbo and mini receive rings.
- Allocates the receive return ring and points firmware at receive-return producer indexes.
- Points firmware statistics refresh at `gib->statistics`.
- Programs DMA read/write configuration.
- Sets transmit buffer ratio.
- Sets default coalescing/timer values:
  - `rct = 1`
  - `sct = 0`
  - `st = 1000000`
  - `smcbd = Nsr/4`
  - `rmcbd = 4`
- Enables DMA assist logic.
- Configures gigabit and 10/100 link negotiation registers.
- Sets interface index and MTU.
- Unmasks interrupts through `Mi` and `Hi`.
- Starts firmware by writing `CPUApc = tigon2FwStartAddr` and clearing `CPUhalt`.

The ring sizes are fixed in enums: event ring 256, command ring 64, send ring 512, standard receive ring 512, jumbo ring 256, mini ring 1024, and receive-return ring 2048. Only the standard receive ring is actively replenished; jumbo and mini rings are disabled.

## Transmit Path

`_ga620transmit()` owns actual transmit work under `ctlr->srlock`:

1. Frees completed send blocks between the host cleanup index `sci[2]` and firmware-updated send consumer index `sci[0]`.
2. Computes the usable send-ring space by leaving one descriptor free.
3. Drains `edev->oq` into send descriptors.
4. Converts block addresses to PCI host addresses with `sethost64()`.
5. Stores `BLEN(bp)<<16 | Fend` into each descriptor.
6. Records each `Block*` in `ctlr->srb`.
7. Updates the send producer index `Spi`.

`ga620transmit()` is the `Ether` callback wrapper. Interrupt handling also calls `_ga620transmit()` so completions and pending outbound packets are serviced together.

## Receive Path

`ga620replenish()` tops up the receive standard ring to `NrsrHI` by allocating `ETHERMAXTU+4` blocks, writing receive descriptors, storing the block pointer in `opaque`, incrementing `nrsr`, and updating `Rspi`.

`ga620receive()` consumes receive-return descriptors while `rrrci != rrrpi[0]`:

- Retrieves the returned descriptor and length.
- Delivers valid nonzero non-error frames with `etheriq`.
- Frees errored or zero-length blocks.
- Clears `opaque`.
- Decrements the source ring fill count based on `Frjr`, `Frmr`, or standard-ring default.
- Advances the receive-return consumer index.

Frame-level errors are not manually tallied in the receive path because firmware statistics are exposed through `ga620ifstat()`.

## Event And Interrupt Handling

`ga620interrupt()` first checks the `Is` bit in `Mhc`. If set, it:

- Records cycle count timing.
- Increments interrupt count.
- Writes `Hi = 1` to mark host interrupt handling.
- Loops over receive completions, transmit cleanup/fill, event processing, and receive-ring replenishment.
- Temporarily clears `Hi` when no work is found on the first idle pass.
- Requires two idle checks before leaving.
- Adds elapsed cycles to `ctlr->ticks`.

`ga620event()` consumes firmware event ring entries and handles:

- `0x01` firmware operational: sends command `0x01` to mark host stack up and command `0x0B` to start link negotiation.
- `0x04` statistics updated: no local action.
- `0x06` link-state changed: updates `edev->mbps` for gigabit or 10/100 and prints link up/down messages.
- `0x07` and unknown events: print diagnostics.

Event consumer index `Eci` is updated after events are processed.

## Runtime Controls And Statistics

`ga620ctl()` parses text commands:

- `coalupdateonly on|off`: toggles `CoalUpdateOnly` in the send-ring control block.
- `hardwarecksum on|off`: toggles TCP/UDP checksum and no-pseudo-header checksum flags in send and receive standard ring controls.
- `rct <n>`: writes receive coalesced ticks.
- `sct <n>`: writes send coalesced ticks.
- `st <n>`: writes statistics ticks.
- `smcbd <n>`: writes send max coalesced BDs.
- `rmcbd <n>`: writes receive max coalesced BDs.

Invalid commands return `-1`; successful commands return the input byte count.

`ga620ifstat()` prints nonzero entries from the 256-entry firmware statistics block, then prints interrupt count, interrupt-mask value `mi`, accumulated handler cycles, checksum/coalescing flags, and coalescing/timer tunables.

`ga620promiscuous()` sends firmware command `0x0A` with flag `1` to enable or `2` to disable promiscuous mode. `ga620multicast()` sends firmware command `0x0E` with flag `1` when adding a multicast address; removal is ignored and individual multicast addresses are not tracked in this file.

## Dependencies

This driver depends on:

- Plan 9 kernel headers: `u.h`, `lib.h`, `mem.h`, `dat.h`, `fns.h`, `io.h`, `error.h`, `netif.h`
- Generic ethernet declarations from `etherif.h`
- Embedded firmware data from `etherga620fw.h`
- PCI discovery/configuration: `pcimatch`, `pcicfgr8`, `pcicfgw8`, `Pcidev`, PCI BAR metadata
- Memory mapping: `vmap`, `vunmap`
- DMA address helpers: `PCIWADDR`
- Allocation helpers: `malloc`, `free`, `xspanalloc`, `iallocb`, `freeb`
- Queue and packet delivery: `qget`, `etheriq`
- Timing: `microdelay`, `cycles`
- Command parsing/stat helpers: `parsecmd`, `readstr`, `snprint`
- Generic ethernet registration: `addethercard`

## Review Notes

- The driver is tightly coupled to firmware structure layout. Any change to `Gib`, `Rcb`, `Rbd`, `Sbd`, ring sizes, command/event meanings, or byte-swap settings must be validated with the included firmware image.
- `ga620pci()` does not unmap BAR memory if `ga620reset()` fails after `vmap`; it frees the controller but leaves the mapping.
- `ga620pci()` also calls `error(Enomem)` if `Ctlr` allocation fails after `vmap`, but the `vunmap()` just before that is present only for the allocation-failure branch, not for later reset failure.
- `ga620init()` uses `waserror()` to free several allocations on failure, but only the pointers initialized before the error are covered. The receive-return ring allocation happens immediately before `poperror()`, so later initialization failures would not be handled by that cleanup block.
- Runtime `ga620ctl()` mutates shared firmware-visible ring control blocks and CSR tunables without explicit locking against interrupts or firmware access.
- `ga620attach()` is intentionally empty; firmware startup is driven during `ga620init()` and operational events rather than attach.
- `ga620shutdown()` prints unconditionally before detaching, which can be noisy during ordinary shutdown.
- The mini and jumbo receive rings are defined but disabled. MTU/jumbo changes require more than changing `IfMTU`.
- `ga620multicast()` enables multicast on additions but ignores removals and does not maintain a filter list.

## Research Guidance

Treat this file as a host/firmware contract. The highest-risk edits are in ring initialization, endian/DMA configuration, interrupt-loop quiescence, producer/consumer index handling, and firmware command/event interpretation. For behavioral changes, inspect `etherga620fw.h` and any firmware-generation provenance before changing shared structures or constants. For performance tuning, prefer runtime `ga620ctl()` parameters first, then validate with receive-ring fill levels, send completion behavior, and interrupt coalescing statistics.

# File Research: sources/os/plan9/9front/sys/src/9/pc/etherga620.c

## Purpose

This file is the Plan 9/9front PCI ethernet driver for Netgear GA620, GA620T, Alteon AceNIC, DEC DEGPA-SA, and SGI AceNIC adapters built around the Alteon Tigon 2 gigabit ethernet controller. It provides the host-side driver glue, PCI discovery, device reset, firmware upload, ring setup, interrupt handling, transmit/receive paths, link-state handling, EEPROM MAC address reads, and generic `Ether` registration.

It includes `etherga620fw.h` directly and loads the embedded Tigon2 firmware into NIC local memory during reset.

## Main Interfaces

- `etherga620link()` registers the card name `GA620` with the generic ethernet layer via `addethercard`.
- `ga620pnp()` binds an unused detected controller to an `Ether`, initializes hardware, installs callbacks, and enables interrupts.
- `ga620transmit()`, `ga620interrupt()`, `ga620receive()`, `ga620ctl()`, `ga620ifstat()`, `ga620promiscuous()`, `ga620multicast()`, and `ga620shutdown()` are the operational driver hooks.
- `ga620pci()` scans PCI devices and builds the controller list.
- `ga620reset()` and `ga620init()` split hardware reset/firmware-load work from runtime ring and mailbox initialization.

## Core Data Structures

The driver models the Tigon host/NIC ABI explicitly:

- `Host64` stores high/low halves of PCI-visible host addresses.
- `Ere` is an event ring element.
- `Rbd` is used for receive descriptors and receive-return descriptors, including an `opaque` pointer that carries the Plan 9 `Block*`.
- `Sbd` is a send descriptor.
- `Rcb` is a firmware ring-control block.
- `Gib` is the General Information Block shared with firmware, containing statistics, all ring control blocks, and host-addressed producer/consumer pointer locations.
- `Ctlr` holds PCI identity, MMIO base, MAC address, shared structures, ring pointers, ring indexes, counters, and tunables.

The ring sizes are fixed to the firmware/NIC interface: 256 event entries, 64 command entries, 512 send entries, 512 standard receive entries, 256 jumbo receive entries, 1024 mini receive entries, and 2048 receive-return entries. Jumbo and mini receive rings are disabled in this driver.

## Control Flow

PCI discovery in `ga620pci()` matches ethernet-class PCI devices against known vendor/device IDs, maps BAR0 with `vmap`, enables PCI, calls `ga620reset()`, enables bus mastering, and queues each controller on `ctlrhead`.

Reset in `ga620reset()` hard-resets the adapter, forces little-endian operating mode, configures SRAM and PCI state, reads the station address from the AT24C32 serial EEPROM, and uploads firmware sections:
- text to `tigon2FwTextAddr`
- rodata to `tigon2FwRodataAddr`
- data to `tigon2FwDataAddr`
- zeroed sbss and bss regions

Runtime initialization in `ga620init()` programs the MAC address, allocates the GIB and host rings, writes ring control blocks, configures DMA, coalescing, link negotiation, MTU, interrupt masks, and finally starts firmware by writing `CPUApc` and clearing `CPUhalt`.

Transmit in `_ga620transmit()` first frees completed send blocks using the firmware-updated send consumer index, then drains `edev->oq` into available send descriptors, records each `Block*` in `ctlr->srb`, and updates `Spi`.

Receive in `ga620receive()` walks the receive-return ring until `rrrci == rrrpi[0]`, delivers valid standard-frame blocks with `etheriq`, frees errored blocks, clears descriptor opacity, decrements the matching receive-ring fill count, and advances the consumer index. `ga620replenish()` tops the standard receive ring back to `NrsrHI`.

Interrupt handling in `ga620interrupt()` acknowledges ownership through `Hi`, loops over receive, transmit completion, event processing, and receive replenishment until no more work is found, then unmasks/clears the host interrupt. It measures handler cycles into `ctlr->ticks`.

Firmware events in `ga620event()` handle operational startup, statistics refresh, link-state changes, and unknown/error events. On firmware-up, the driver sends commands to mark the host stack up and start link negotiation.

## Configuration and Diagnostics

`ga620ctl()` accepts runtime text commands:
- `coalupdateonly on|off`
- `hardwarecksum on|off`
- `rct <n>`
- `sct <n>`
- `st <n>`
- `smcbd <n>`
- `rmcbd <n>`

`ga620ifstat()` dumps nonzero firmware statistics and driver counters/tunables.

Promiscuous mode sends command `0x0a`; multicast add enables multicast reception with command `0x0e`. The multicast hook does not track individual multicast addresses and does nothing on removal.

## Dependencies

This is tightly coupled to the Plan 9 PC kernel ethernet stack and PCI support:
- `etherif.h`, `netif.h`, `pci.h`, `io.h`, `dat.h`, `fns.h`
- Plan 9 block queues and packet delivery: `qget`, `Block`, `freeb`, `iallocb`, `etheriq`
- PCI and MMIO helpers: `pcimatch`, `pcienable`, `pcisetbme`, `pcicfgw8`, `vmap`
- CPU timing and delays: `cycles`, `microdelay`
- Firmware constants and arrays from `etherga620fw.h`

## Notable Risks

- `ga620init()` allocates GIB/rings with `malloc`/`malign` but does not check every allocation before writing through pointers.
- `ga620pci()` leaks a mapped BAR if `Ctlr` allocation fails after `vmap`.
- `ga620shutdown()` prints unconditionally, which can be noisy during normal shutdown.
- Runtime `ga620ctl()` mutates firmware ring-control fields without explicit synchronization against interrupts or firmware access.
- Hardware checksum toggles only update ring-control flags; existing descriptors or firmware state are not drained/reinitialized.
- Jumbo and mini rings are disabled; the driver is standard-MTU only despite supporting Tigon2 gigabit hardware.
- EEPROM access is bit-banged by command strings; malformed strings return `-1`, but call sites assume the hardcoded protocol is correct.
- The interrupt loop uses a fixed two-pass idle check; unusual firmware producer update races could delay work until a later interrupt.
- Firmware is opaque generated data, so source-level auditing of NIC behavior is not possible from this file alone.

## Testing Notes

No executable tests were run for this research pass. Useful verification would require either real supported PCI hardware or an emulator/model with Tigon2 register behavior. Static checks should focus on allocation failure paths, ring index invariants, interrupt masking, and whether checksum/offload control changes need quiescing.

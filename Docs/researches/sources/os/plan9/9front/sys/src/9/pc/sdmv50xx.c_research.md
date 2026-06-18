# File Research: sources/os/plan9/9front/sys/src/9/pc/sdmv50xx.c

## Role

SD driver for Marvell 88SX50xx/60xx SATA host controllers, covering 4-port and 8-port PCI/PCI-X SATA I/II controllers with Marvell EDMA request/response rings.

## Main Interfaces

- Exports `SDifc sdmv50xxifc` named `mv50xx`.
- PnP path `mv50pnp()` matches Marvell vendor `0x11ab` and selected 5040/5041/5080/5081/6041/6081 devices.
- Runtime callbacks include `mv50enable`, `mv50disable`, `mv50verify`, `mv50online`, `mv50rio`, `mv50bio`, `mv50rctl`, `mv50wctl`, and `mv50ata`.

## Key Behavior

- Maps controller MMIO, models chip/drive EDMA register sets, allocates Tx/Rx command queues and PRD tables per drive.
- Maintains a hotplug state machine: `Dnull`, `Dnew`, `Dready`, `Derror`, `Dmissing`, and `Dreset`.
- `satakproc()` periodically checks port status, handles inserted/removed disks, resets unstable links, and identifies new drives.
- `identifydrive()` performs IDENTIFY via PIO registers, extracts geometry and strings, and enables EDMA.
- `mv50bio()` submits read/write SRBs, chunks transfers to 128 sectors because PRD count is 16-bit, waits for completion, and retries reset/re-enable paths.
- `mv50ata()` supports limited raw ATA pass-through for PIO/no-data protocols and FIS signature queries.

## Dependencies And Assumptions

- Depends on Plan 9 SD and `<fis.h>` helpers for ATA identity and FIS handling.
- Uses many Marvell-specific magic values and errata workarounds for PHY calibration, SATA I/II mode toggling, and error handling.
- Uses 32-bit DMA addresses in PRDs.
- ATAPI/queued DMA support is not a focus; request handling is centered on disk read/write and limited pass-through.

## Research Notes

- The driver is heavily hotplug-aware compared with `sdide.c`.
- EDMA queue management is simple and bounded: 31 active slots plus a software pending list.
- Comments and branch names make clear that several behaviors were reverse-engineered or errata-driven.

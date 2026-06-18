# File Research: sources/os/plan9/plan9/sys/src/9/pc/sdmv50xx.c

Purpose: Plan 9 `SDifc` driver named `mv50xx` for Marvell 88SX50xx/60xx SATA controllers, especially multi-port fileserver cards. It implements controller discovery, EDMA ring setup, SATA PHY/reset handling, drive identify, interrupt completion, and read/write SD I/O.

Main structures:
- `Ctlr`: PCI/MMIO controller state, chips, drives, interrupt identity, mapped register windows.
- `Chip`: group of four ports, with `Arb` and `Edma` register blocks.
- `Drive`: per-port state, `SDunit`, bridge/EDMA register pointers, SATA mode/state, identity data, EDMA rings, outstanding SRB table and queue.
- `Srb`: software request buffer representing one read/write command.
- `Prd`, `Tx`, `Rx`: card-visible DMA descriptor, request, and response entries.

Key logic:
- `mv50pnp` scans Marvell vendor devices, accepts supported device IDs, maps BAR0, initializes chip/port register pointers, and creates an `SDev`.
- `mv50verify` configures a unit/drive, initializes EDMA memory, applies type-specific interrupt masks and PHY state, resets the disk, and unmasks interrupts.
- `resetdisk`, `phyerrata`, and `enabledrive` handle Marvell-specific EDMA reset and SATA PHY tuning.
- `identifydrive` issues ATA identify via programmed I/O, parses LLBA support, sector count, model/firmware/serial, fills inquiry data, and transitions the drive to ready.
- `startsrb` writes one EDMA request entry and PRD, fills ATA registers through `mvsatarequest`, advances the request ring, and tracks the SRB by command ID.
- `completesrb` drains response entries, marks SRBs done/error, wakes waiters, and starts queued SRBs.
- `mv50interrupt` decodes per-port interrupt cause, updates drive state, and drains completed SRBs.
- `satakproc` periodically runs `checkdrive`, handling new/missing/error/reset states and retrying mode/reset/identify.
- `mv50rio` accepts SCSI read/write(10), uses `sdfakescsi` for metadata commands, chunks I/O to 128 sectors, submits SRBs, waits for completion, and retries failed/no-completion requests.
- `mv50rctl` dumps model/serial/firmware, geometry, identity words, and controller/arb/bridge/EDMA registers.

Dependencies and integration:
- Uses Plan 9 SD layer through `SDifc sdmv50xxifc`.
- Relies on PCI matching, MMIO mapping, interrupt registration, `sdfakescsi`, Plan 9 kernel sleeps/wakeups, and physical address macros.

Risks and notes:
- EDMA PRD byte count is 16-bit, so I/O is limited to 128 sectors per SRB.
- PHY errata code contains hardware magic and revision-specific behavior; it is fragile but likely necessary for these controllers.
- `enabledrive` assigns `d->bridge->status = 0x113` inside an `if`, forcing `Dnew`; this is noteworthy and may be deliberate hardware forcing, but reads like a bug.
- No ATAPI path is implemented; only disk read/write and faked SCSI metadata are handled.

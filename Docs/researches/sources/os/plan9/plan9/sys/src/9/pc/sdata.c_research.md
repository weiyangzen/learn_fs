# File Research: sources/os/plan9/plan9/sys/src/9/pc/sdata.c

Purpose: Plan 9 `SDifc` driver named `ata` for legacy ATA/ATAPI controllers on PC hardware. It supports legacy ISA-style ATA ports, PCI IDE controllers, ATA disks, ATAPI packet devices, PIO transfers, bus-master DMA, read/write-multiple, 28-bit and 48-bit LBA.

Main structures:
- `Ctlr`: ATA channel state, command/control ports, IRQ, PCI/bus-master data, current drive, interrupt counters, PRD table, register lock.
- `Drive`: per-device ATA/ATAPI identity, geometry, sector count, DMA/RWM capability flags, packet command buffer, fake SCSI sense/inquiry data, active transfer state.
- `Prd`: bus-master IDE physical region descriptor.

Key logic:
- `atapnp`, `ataprobe`, `atadrive`, `ataidentify` detect legacy and PCI IDE channels, distinguish ATA from ATAPI, parse identify words, and build `SDev` instances.
- `ataenable` allocates PRD memory for bus-master DMA, enables PCI bus mastering, registers interrupts, and enables channel interrupts.
- `atario` converts SD requests into ATA or ATAPI operations. It rewrites SCSI read/write(6) to read/write(10), forwards ATAPI packets, and emulates SCSI commands for ATA disks.
- `atagenio` handles ATA disk commands: test-unit-ready, request sense, inquiry, read capacity, read/write(10/16), mode sense, and split transfers by controller limit.
- `atageniostart` programs ATA registers for CHS/LBA/LBA48 and selects DMA, read/write multiple, or sector PIO.
- `atapktio` issues ATAPI packet commands with optional DMA and interrupt-driven packet/data phases.
- `atainterrupt` dispatches PIO read/write, packet, DMA, and standby completions, records status/error, clears current drive, and wakes waiters.
- `atawctl` exposes runtime controls: `dma on/off`, `rwm on/off`, `standby`, and `lba48always`.

Dependencies and integration:
- Uses Plan 9 SD layer via `SDifc sdataifc`.
- Uses PCI helpers (`pcimatch`, `pcicfgr*`, `pcisetbme`), ISA I/O allocation, interrupt registration, SCSI helper functions (`scsiverify`, `scsionline`, `scsibio`), and port I/O helpers (`inb`, `outb`, `inss`, `outss`).
- Contains controller-specific PCI quirks for Intel ICH, Promise, Silicon Image, VIA, AMD, NVIDIA, ATI, HighPoint, CMD, ServerWorks, and others.

Risks and notes:
- DMA setup assumes physically contiguous/valid PCI addresses and splits only by controller span; bad mappings or boundary assumptions can fail I/O.
- Many hardware timing loops are fixed microsecond/millisecond waits; marginal disks may time out or require reset.
- ATAPI DMA has fallback and disables DMA after repeated trouble, but error recovery is mostly abort/reset based.
- Several debug paths are compile-time gated by `DEBUG`; normal diagnostics are sparse unless flags change.

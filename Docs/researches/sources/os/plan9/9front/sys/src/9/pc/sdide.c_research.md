# File Research: sources/os/plan9/9front/sys/src/9/pc/sdide.c

## Role

Plan 9/9front SD block driver for legacy ATA/ATAPI IDE controllers, including PCI IDE compatibility/native modes, bus-master DMA, PIO, ATAPI packet devices, SCSI-emulated block requests, and raw ATA pass-through.

## Main Interfaces

- Exports `SDifc sdideifc` named `ide`.
- PnP path: `atapnp()` scans PCI storage controllers and falls back to legacy channels at `0x1f0/0x170`.
- Configured probe path: `ataprobew()` supports explicit controller configuration.
- Runtime callbacks: `ataenable`, `atadisable`, `ataonline`, `atario`, `atarctl`, `atawctl`, `ataclear`, `atastat`, and `ataataio`.

## Key Behavior

- Implements ATA register definitions, IDENTIFY parsing, CHS/LBA/LBA48 addressing, read/write multiple, bus-master PRD DMA, and ATAPI packet transfer.
- `atadrive()` detects ATA vs ATAPI, fills model/serial/firmware, sets FIS signature metadata, sector count, sector size, DMA capabilities, and SCSI inquiry strings.
- `atagenio()` translates standard SD/SCSI read-write commands through `sdfakescsi()` and `sdfakescsirw()`, chunks transfers by controller limits, and retries by disabling DMA or read/write multiple.
- `atapktio()` handles ATAPI packet commands with optional DMA and byte-count-limited PIO data phases.
- `ataataio()` handles raw ATA/FIS-like pass-through, sanitizing host-to-device FIS fields and supporting an out-of-band signature query command.
- Interrupt handling dispatches PIO, DMA, packet, no-data, and reset completions, with missed-interrupt polling fallback in `iowait()`.

## Dependencies And Assumptions

- Depends on Plan 9 SD, PCI, SCSI emulation, and `<fis.h>` ATA/FIS helper functions.
- DMA is passive: BIOS or prior firmware is assumed to have selected valid transfer modes.
- PRD setup assumes DMA buffers are suitably aligned and uses 32-bit PCI addresses.
- Device/controller quirks are encoded through a large PCI ID switch, including Intel ICH, Promise, SiI, VIA, AMD/ATI, Nvidia, Marvell, JMicron, and others.

## Research Notes

- This is the central fallback driver for non-AHCI ATA storage in the PC kernel.
- Error handling is intentionally pragmatic: timeouts abort with NOP or software reset, and repeated failures progressively fall back to simpler transfer modes.
- Several hardware quirks and comments show this driver is compatibility-oriented rather than a clean ATA abstraction.

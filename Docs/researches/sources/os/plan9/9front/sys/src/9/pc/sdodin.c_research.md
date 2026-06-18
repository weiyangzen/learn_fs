# File Research: sources/os/plan9/9front/sys/src/9/pc/sdodin.c

## Role

SD driver for Marvell Odin II 88SE64xx SATA/SAS controllers. It supports SATA disks, ATAPI packet devices, SAS SSP devices, hotplug state tracking, raw SATA pass-through, and enclosure LED integration.

## Main Interfaces

- Exports `SDifc sdodinifc` named `odin`.
- PnP path `mspnp()` matches Marvell vendor `0x11ab`, device `0x6485`.
- Runtime callbacks include `msenable`, `msdisable`, `msverify`, `msonline`, `msrio`, `msrctl`, `mswctl`, `mswtopctl`, and `msataio`.

## Key Behavior

- Initializes Odin delivery/completion queues, command headers, FIS receive buffer, command tables, and port register windows.
- Uses per-drive state flags for missing, no-power, new, ready, error, reset, offline, and port reset.
- `mskproc()` periodically calls `checkdrive()` to handle PHY status, spin-up, reset, identify/probe, removal, and retry timing.
- SATA path builds ATA register FISes with PRDT entries and uses `<fis.h>` helpers for read/write, identify, set-features, set-transfer-mode, and flush-cache commands.
- ATAPI path builds packet FISes and reports actual transfer length through received FIS data.
- SAS path builds open-address frames and SSP command IUs, parses response/sense data, reads inquiry/VPD/capacity, and maps SAS devices into SD units.
- Interrupt handler processes central, port, command-set, and completion interrupts, wakes command waiters, and marks commands for retry/reset/error based on completion and port error state.
- LED support adds a per-unit `led` file and drives SGPIO LED patterns through `../port/led.h` helpers.

## Dependencies And Assumptions

- Depends on Plan 9 SD/SCSI, PCI, `<fis.h>`, and LED infrastructure.
- Uses 32-bit PCI DMA high-address stubs (`Pciwaddrh(a) 0`), so it assumes usable low DMA addressing.
- Several comments mark uncertain hardware behavior and “wormhole” register accesses.
- Command concurrency is one command object per port, not a deep queue per disk.

## Research Notes

- This is the richest storage driver in this group: it bridges ATA-like SATA, packet ATAPI, and SAS SSP command models.
- Error classification intentionally separates “no verdict” retry paths from definite I/O errors.
- The file doubles as controller support and enclosure-management glue through SGPIO LEDs.

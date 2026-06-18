# File Research: sources/teaching/minix/minix/drivers/storage/at_wini/at_wini.c

## Purpose
Implements the legacy MINIX IBM-AT Winchester/ATA/ATAPI disk driver. It handles PCI IDE controllers, compatibility/native channels, PIO and bus-master DMA transfers, ATAPI CD reads, partition exposure, timeouts, resets, and a small ioctl set.

## Main Flow
Startup initializes SEF, registers live update callbacks, allocates temporary/DMA buffers, parses boot parameters, probes a PCI IDE device by instance, initializes up to four drive slots across primary and secondary channels, registers native or compatibility IRQs, enables bus mastering, announces the block driver, and runs `blockdriver_task()`.

`w_do_open()` maps the minor to a drive/partition, identifies the drive on first open or after deafness, tests ATA I/O for non-ATAPI devices, denies writes to ATAPI, opens ATAPI media if needed, and calls `partition()` on first open.

## Key Behavior
- Supports up to four actual drives per controller instance and exposes up to eight drive-node groups.
- `w_identify()` first tries ATA IDENTIFY, then ATAPI IDENTIFY, parses CHS/LBA/LBA48 capacity, detects DMA support, and sets state flags.
- ATA transfers use `w_transfer()`:
  - Enforces sector-aligned position and size.
  - Clips at partition EOF.
  - Uses DMA when supported and possible; otherwise falls back to PIO.
  - Retries transient errors up to `max_errors`.
  - Updates iovec progress and returns partial total at EOF.
- DMA setup builds a PRDT, rejects unaligned buffers, splits entries at 64 KiB boundaries, and disables DMA when hardware status indicates bad behavior.
- PIO path waits for IRQ/status per sector and uses safe word I/O to copy between grants and device data register.
- ATAPI path supports read-only CD-style `SCSI_READ10`, optional DMA, partial-sector discard/copy handling around 2048-byte sectors, sense debug output, and packet phase interpretation.
- Timeout handling marks controllers deaf, reduces maximum transfer count after read/write timeouts, and can ignore devices during probe/testing.
- Reset toggles the control reset bit, waits for readiness, clears `DEAF`, and reenables native IRQs.
- Ioctls implement `DIOCTIMEOUT`, `DIOCOPENCT`, and ATA `DIOCFLUSH`.

## Integration Notes
This file depends on `at_wini.h` for register definitions, state flags, identify offsets, DMA constants, and live update callback declarations. It uses MINIX PCI, IRQ, safe I/O, grant, partition, timer/alarm, and blockdriver APIs.

## Risks
The driver uses shared globals (`w_wn`, `w_drive`, `w_command`, `w_dv`) and a synchronous command model, making it sensitive to message ordering and live update timing. DMA fallback, PRDT sizing, timeout recovery, and ATAPI partial-sector logic are the highest-risk areas.

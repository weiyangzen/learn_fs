# File Research: sources/teaching/minix/minix/drivers/storage/ahci/ahci.c

## Purpose
Implements the MINIX AHCI block driver for SATA ATA/ATAPI devices. It is a multithreaded `libblockdriver_mt` disk driver with hotplug handling, device identification, partition exposure, NCQ support, cache-control ioctls, and AHCI HBA/port management.

## Main Flow
Startup enters `main()`, calls `sef_local_startup()`, then runs `blockdriver_mt_task()`. Fresh initialization parses environment parameters, probes a PCI AHCI device by instance number, maps BAR6 MMIO registers, registers the IRQ, resets and enables the HBA, initializes implemented ports, and builds the device-to-port map.

Each port starts in a state machine covering `SPIN_UP`, `NO_DEV`, `WAIT_DEV`, `WAIT_ID`, `BAD_DEV`, and `GOOD_DEV`. Port interrupts and timers drive transitions for attach, detach, identify completion, readiness polling, command timeout, and fatal error recovery.

## Key Behavior
- Supports up to 32 AHCI ports and exposes at most 8 drive nodes for compatibility with `at_wini` minor numbering.
- Handles ATA fixed disks and removable ATAPI devices.
- Uses AHCI command lists, command tables, FIS construction, and PRDT entries.
- Uses NCQ when both HBA and device support it; queue depth is bounded by HBA command slots and device queue depth.
- Caps a single transfer at `MAX_TRANSFER`/4 MiB to keep PRD handling, timeout policy, and client-induced latency bounded.
- Supports sector-unaligned reads by using a padding buffer for leading/trailing sectors; writes must be sector-aligned.
- Uses `sys_vumap()` to map client grants into physical PRDs and rejects non-contiguous or unaligned physical mappings.
- On first open, clears any hotplug barrier, checks ATAPI media if needed, resets partition tables, sets whole-device size, calls `partition()`, and raises worker count to the port queue depth.
- On close of the last open, reduces workers to one and flushes write cache if the device is still good and not behind a barrier.
- Implements `DIOCEJECT`, `DIOCOPENCT`, `DIOCFLUSH`, `DIOCSETWC`, and `DIOCGETWC`.
- Delays termination on `SIGTERM` until all opened ports close, then stops the HBA and terminates the blockdriver loop.

## Device And Error Handling
- `port_connect()` starts a port and launches identify.
- `port_id_check()` validates ATA/ATAPI identify data and fills LBA count, sector size, cache/FUA flags, NCQ flags, and read-only state.
- `port_disconnect()` fails outstanding requests, marks a barrier, disables extra workers, and forces upper layers to close/reopen before accessing a replacement device.
- `port_restart()` fails current commands and either restarts the port or disconnects and hard-resets when BSY/DRQ remain set.
- Interrupt handling completes successful commands before processing failures; NCQ failures conservatively fail all remaining pending commands.

## Integration Notes
This file depends on MINIX PCI access, VM physical mapping, IRQ policy calls, timers, `libblockdriver_mt`, partition parsing, safecopy grants, and AHCI/ATA/ATAPI register definitions from `ahci.h`.

## Risks
The correctness boundary is hardware state coordination: timer/interrupt races, hotplug barriers, NCQ failure attribution, PRD construction from grants, cache flush failures, and the assumption that HBA command slots fit in 32-bit masks.

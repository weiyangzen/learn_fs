# File Research: sources/teaching/minix/minix/drivers/storage/filter/driver.c

## Purpose
Implements the filter driver’s lower layer: backing-driver discovery, open/close, asynchronous request forwarding, mirror coordination, timeout handling, restart/refresh recovery through RS, and DS event processing.

## Main Flow
`driver_init()` resolves the configured main driver endpoint, opens it, retrieves partition size, and optionally does the same for a backup mirror driver. `read_write()` is the exported I/O entry point used by checksum logic: it creates grants, sends gather/scatter requests to one or both backing drivers, validates replies, adjusts returned size for EOF, and reports retry/recovery conditions.

## Key Behavior
- Maintains two `driverinfo` records: main and backup.
- `driver_open()` sends `BDEV_OPEN`, then `DIOCGETP`, and validates raw partition size consistency between mirrored disks.
- `bad_driver()` records `BD_DEAD`, `BD_PROTO`, or `BD_DATA` plus an error code and asks callers to redo.
- `check_driver()` decides whether to retry, refresh/restart through RS, disable mirroring, or return an error to the user.
- `restart_driver()` sends `RS_REFRESH` when needed and waits for DS block-driver-up events.
- Request forwarding uses `ipc_senda()` plus `driver_receive()` to avoid blocking on both mirror drivers sequentially when labels differ.
- `flt_receive()` handles DS notifications, CLOCK timeout notifications, stray messages, and reply source matching.
- Paired requests go to both drivers for mirrored writes and dual reads, but only to the main driver for normal reads.
- Grant helpers split large transfers into chunks when `CHUNK_SIZE` is configured and revoke all grants after completion.
- Reply validation treats invalid message types, negative status, suspicious truncation, and timeout as driver problems.

## Integration Notes
This file is called by `sum.c` through `read_write()` and by `main.c` for lifecycle (`driver_init()`, `driver_shutdown()`), size (`get_raw_size()`), retry reset, and DS event dispatch. It depends on DS, RS, asynchronous IPC, safecopy grants, and MINIX blockdriver message formats.

## Risks
The driver recovery state machine is subtle: timeout attribution, old alarm filtering, pending DS events, mirrored request ordering, endpoint replacement, and mirror disablement all affect data availability. Blocking `ipc_sendrec()` in open/close is explicitly called unfinished.

# File Research: sources/teaching/minix/minix/drivers/storage/filter/main.c

## Purpose
Implements the top-level blockdriver interface, configuration parsing, SEF lifecycle, and caller-buffer copying for the filter driver.

## Main Flow
Startup registers SEF callbacks, parses a single option string, allocates the main buffer, initializes checksum support, initializes lower drivers, subscribes to DS block-driver events, announces the service, and runs `blockdriver_task()`.

I/O enters `filter_transfer()`: it validates sector alignment, allocates a buffer, copies write data in from caller grants, calls `transfer()` from the checksum/layout layer with retry loops around `RET_REDO`, copies read data back on success, frees the buffer, and returns the transferred size.

## Key Behavior
- Configuration options include main/backup labels and minors, checksum layout settings, mirror enablement, checksum type, checksum error policy, retry/restart counts, timeout, and chunk size.
- `USE_CHECKSUM` implies `USE_SUM_LAYOUT`.
- Determines checksum storage size from checksum type:
  - nil: 4 bytes;
  - xor: 16 bytes;
  - crc: 4 bytes;
  - md5: 16 bytes.
- Rejects invalid label/minor configuration and impossible checksum-sector packing.
- `filter_ioctl()` supports `DIOCGETP` by returning logical size through `convert(get_raw_size())`.
- Rejects `DIOCSETP`, `DIOCTIMEOUT`, and `DIOCOPENCT`; unknown ioctls return `ENOTTY`.
- `filter_other()` forwards DS notifications to `ds_event()`.
- `SIGTERM` triggers `driver_shutdown()` and exits.

## Integration Notes
This file is the public blockdriver layer. It delegates data integrity and layout conversion to `sum.c`, backing-driver operations to `driver.c`, and allocation helpers to `util.c`.

## Risks
The driver copies complete requests into an intermediate buffer, so memory pressure scales with request size. It ignores the incoming transfer `flags`, so lower-layer force-write or similar flags are not propagated from callers.

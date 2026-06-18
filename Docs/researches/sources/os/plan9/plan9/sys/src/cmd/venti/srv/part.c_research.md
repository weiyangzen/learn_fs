# File Research: sources/os/plan9/plan9/sys/src/cmd/venti/srv/part.c

Purpose: Wraps file/device partitions with optional byte-range slicing and bounded I/O.

Key behavior:
- Parses names like `file:lo-hi`, with `k/m/g/t` suffixes.
- `initpart` opens the backing file/device, applies global read-only mode, validates range bounds, and records partition size/offset.
- `rwpart` checks partition bounds and performs chunked `pread`/`pwrite` operations capped at `Maxxfer`.
- `readpart` and `writepart` are simple wrappers.
- `readfile` loads an entire partition/file into a `ZBlock`.

Dependencies:
- Uses Plan 9 file APIs, `Dir`, `ZBlock`, and Venti allocation/error helpers.

Notable details:
- `flushpart` is a no-op in this implementation.
- `Maxxfer` is 64 KiB, documented as a workaround for old NCR SCSI controller limits.

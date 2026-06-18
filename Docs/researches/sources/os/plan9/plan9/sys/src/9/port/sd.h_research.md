# File Research: sources/os/plan9/plan9/sys/src/9/port/sd.h

Defines the generic Plan 9 storage-device framework.

Core structures:
- `SDperm`: name/user/permission triple.
- `SDpart`: partition start/end, permissions, validity, version.
- `SDunit`: a unit/LUN with inquiry/sense data, geometry, partitions, raw request state, and permissions.
- `SDev`: controller/device instance with interface, controller private data, unit array, and enable state.
- `SDifc`: controller method table: probe, enable/disable, verify, online, raw I/O, control read/write, block I/O, clear, top-level control.
- `SDreq`: SCSI-like request with command bytes, data buffer, status, transfer length, and sense data.
- `SDio`: host-controller interface for MMC/SD/SDIO.

Constants:
- SCSI inquiry bits and peripheral type values.
- SD status codes, retry/malloc/timeout values, `SDmaxio`, and default partition count.
- Default `sdmalloc`/`sdfree` wrappers, overridable for DMA alignment.

Exports:
- Device registry helpers from `devsd.c`.
- SCSI helpers from `sdscsi.c`.

Role:
- Common storage abstraction used by AoE, MMC, SCSI, and device-layer storage code.

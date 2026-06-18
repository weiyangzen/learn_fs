# File Research: sources/virtualization/nbdkit/plugins/vddk/vddk-structs.h

Defines local copies of VDDK API types, constants, enums, and structs needed by the plugin, updated to VDDK 7.0 fields.

Key contents:
- Error constants: `VIX_OK`, `VIX_E_FAIL`, `VIX_E_NOT_SUPPORTED`, `VIX_ASYNC`.
- Open flags for unbuffered, single-link, read-only, and compression modes.
- Sector size constant `VIXDISKLIB_SECTOR_SIZE` and QueryAllocatedBlocks chunk limits.
- Disk type enum for sparse/flat/split/VMFS/stream-optimized formats.
- Hardware version constants for Workstation and ESX variants.
- Opaque handles: `VixDiskLibConnection`, `VixDiskLibHandle`.
- Log and async completion callback typedefs.
- Credential and spec type enums.
- `VixDiskLibConnectParams`, including UID and session-id credential unions plus vStorage object spec fields.
- Geometry, adapter type, disk info, block list, and create parameter structs.
- `VixDiskLibInfo` includes VDDK 7.0 `logicalSectorSize` and `physicalSectorSize`.

Role:
- Allows the plugin to dlopen/dlsym VDDK without including or linking VMware headers at build time.

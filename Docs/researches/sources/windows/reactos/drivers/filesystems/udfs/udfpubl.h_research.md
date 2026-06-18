# File Research: sources/windows/reactos/drivers/filesystems/udfs/udfpubl.h

This public header defines the IOCTL and data-structure interface between the UDF filesystem driver and user applications or cooperating drivers.

Key contents:
- Defines `IOCTL_UDFFS_BASE` and driver-specific IOCTLs:
  - enable/disable driver
  - invalidate volumes
  - get retrieval pointers
  - get/set file allocation mode
  - lock/unlock volume by PID
  - send license key
  - get special retrieval pointers
  - get version
  - set notification event
  - query just-mounted state
  - register autoformat
  - set options
- Defines input/output structs:
  - `UDF_GET_FILE_ALLOCATION_MODE_OUT`
  - `UDF_LOCK_VOLUME_BY_PID_IN`
  - optional `UDF_GET_SPEC_RETRIEVAL_POINTERS_IN`
  - `UDF_GET_VERSION_OUT`
  - `UDF_SET_OPTIONS_IN`
- Defines public device names:
  - kernel/DOS device `\\DosDevices\\DwUdf`
  - Win32 path `\\\\.\\DwUdf`
- Defines stream names used by UDF support tooling:
  - `UdfIsoBridgeStructure`
  - `DvdWriteNow.cfg`
- Defines user-visible filesystem flags for read-only/raw/media/write-protection states.
- Defines damaged-partition policy constants and option-scope flags for temporary, disk, drive, and global settings.

Notable design points:
- Packing is forced with `#pragma pack(push, 8)` to keep the user/kernel ABI stable.
- Some IOCTLs use `FILE_ANY_ACCESS`, while several operational controls use `FILE_READ_ACCESS`.
- The header is guarded so definitions can coexist with environments that already define CTL_CODE or related filesystem control definitions.

# File Research: sources/windows/reactos/drivers/filesystems/udfs/ntifs_ex.h

## Role

`ntifs_ex.h` is a compatibility header that fills in NTIFS/DDK definitions, prototypes, macros, and constants needed by this UDF driver across Windows/ReactOS build environments.

## Core Contents

- Provides `MmGetSystemAddressForMdlSafer()`, which maps an MDL safely by setting `MDL_MAPPING_CAN_FAIL` around `MmMapLockedPages()` when the MDL is not already system-mapped or nonpaged.
- Defines `FULL_SECURITY_INFORMATION` and declares security descriptor/SID RTL routines used by UDF security support.
- Defines `IsFileObjectReadOnly()`.
- Supplies missing `FSCTL_*` codes, filesystem capability flags, file attribute flags, `FileFs*Information` enum values, `IRP_MN_SURPRISE_REMOVAL`, `VPB_REMOVE_PENDING`, and volume notification event codes when the platform headers do not provide them.
- Declares `ZwFsControlFile()`, `ZwDeviceIoControlFile()`, and `ZwQueryVolumeInformationFile()`.
- Provides fallback definitions for `IoCopyCurrentIrpStackLocationToNext()` and `IoSkipCurrentIrpStackLocation()`.
- Defines a `ptrFsRtlNotifyVolumeEvent` function pointer type and includes `Include/ntddk_ex.h`.

## Dependencies

The header sits between platform DDK/NTIFS headers and the UDF codebase. It depends on MDL, security descriptor, SID, IRP, VPB, FSCTL, and Zw/Nt kernel types being available.

## Notable Risks

- Several blocks are disabled with `#if 0`, so this header documents old compatibility definitions without enabling them.
- The local `MmGetSystemAddressForMdlSafer()` uses older `MmMapLockedPages()` plus temporary MDL flag mutation rather than newer `MmGetSystemAddressForMdlSafe()` semantics.
- Fallback IRP stack macros must match platform behavior exactly; subtle differences can affect pass-through PnP and device-control flows.

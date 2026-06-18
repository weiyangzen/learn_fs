# File Research: sources/windows/reactos/drivers/filesystems/udfs/Include/ntddk_ex.h

Supplemental DDK compatibility header for system information, module/image structures, and storage IOCTL constants.

Key responsibilities:
- Defines `SYSTEM_INFORMATION_CLASS` values used with `ZwQuerySystemInformation()`.
- Declares `ZwQuerySystemInformation()`.
- Defines `SYSTEM_MODULE_ENTRY` and `SYSTEM_MODULE_INFORMATION` for loaded module enumeration.
- Provides basic `WORD`, `BOOL`, `DWORD`, and `BYTE` aliases.
- When not building ReactOS, defines PE/COFF image structures needed for export parsing: DOS header, file header, data directory, optional header, NT headers, and export directory.
- Defines missing disk/storage IOCTL constants such as partition info, drive layout, geometry, load media, media types, and verify checks.

Important behavior:
- The PE image declarations are skipped under `__REACTOS__`, relying on ReactOS headers there.
- `SystemPowerInformation` is conditionally renamed when `PO_CB_SYSTEM_POWER_POLICY` is already present.
- The IOCTL definitions depend on `CTL_CODE`, `IOCTL_DISK_BASE`, `IOCTL_STORAGE_BASE`, method constants, and access constants from included DDK headers.

Dependencies:
- Intended to be included after base NT/DDK definitions that provide `NTSYSAPI`, `NTSTATUS`, `NTAPI`, `PVOID`, `ULONG`, `CHAR`, `LONG`, `USHORT`, and IOCTL macros.

Notable risks:
- This is a compatibility patch header; duplicate definitions can conflict with modern SDK/DDK headers.
- The `SYSTEM_MODULE_ENTRY` layout is historical and version-sensitive.

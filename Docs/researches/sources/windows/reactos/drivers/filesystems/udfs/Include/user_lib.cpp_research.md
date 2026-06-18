# File Research: sources/windows/reactos/drivers/filesystems/udfs/Include/user_lib.cpp

## Purpose
Implements user-mode helper routines shared by UDF/Optical tools around the ReactOS UDFS driver stack. It wraps Win32 service, registry, privilege, event, device-IOCTL, option lookup, and process-launch operations.

## Main Contents
- Defines `MediaTypeStrings[]` matching `JS_DEVICE_TYPE` values from `user_lib.h`.
- Provides small CRT-like helpers: `mymemchr`, `mystrrchr`, `mystrchr`, and `Exist`.
- Implements `MyMessageBox`, including resource-id handling and `FormatMessage` formatting.
- Implements service status lookup with `ServiceInfo`.
- Implements CD-ROM class upper-filter registration checks through `CheckCdrwFilter`.
- Provides registry helpers: `RegisterString`, `RegDelString`, `GetRegString`, `RegisterDword`, `GetRegUlong`, `SetRegUlong`.
- Implements `Privilege` for enabling/disabling token privileges and `IsWow64`.
- Creates globally accessible manual-reset events via `CreatePublicEvent`.
- Sends IOCTLs to a device handle through `UDFPhSendIOCTL`.
- Resolves optical device names with `UDFGetDeviceName`.
- Implements per-option read/write helpers from registry or disk config stream: `GetOptUlong`, `SetOptUlong`, and inherited lookup via `UDFGetOptUlongInherited`.
- Opens a volume with shared read fallback in `OpenOurVolume`.
- Converts drive letters to indexes with `drv_letter_to_index`.
- Launches configured tools with `LauncherRoutine2`.

## Dependencies and Interactions
- Heavy Win32 API use: SCM, registry, process, token, security descriptor, event, message box, file/device handle, and IOCTL APIs.
- Depends on UDFS/optical constants such as `CDROM_CLASS_PATH`, `REG_UPPER_FILTER_NAME`, `CDRW_SERVICE`, `UDF_CONFIG_STREAM_NAME`, `UDF_SERVICE_PARAM_PATH`, `UDF_KEY`, and `IOCTL_CDRW_GET_DEVICE_NAME`.
- Bridges user-mode tools to kernel/driver behavior through `DeviceIoControl`.

## Notable Details
- `UDFGetOptUlongInherited` applies option precedence: global service parameter, device-specific registry key, then disk-specific config stream.
- `UDFGetDeviceName` returns a pointer into a global `RealDeviceName` buffer, so callers must treat the result as non-reentrant shared state.
- `UDFPhSendIOCTL` returns `1` for success and `-1` for failure despite returning `ULONG`; the local `ret = GetLastError()` is not used.
- `GetRegString` opens/query registry data but does not close `hKey` on the success path.

# File Research: sources/windows/reactos/drivers/filesystems/udfs/Include/format_common.h

Public declarations for common UDF formatter UI/device helpers.

Key responsibilities:
- Declares `CheckCDType()` for optical writer/media capability classification.
- Defines the `PADD_DEVICE` callback signature used by device-list population.
- Declares `InitDeviceList()` for enumerating candidate optical drives into a UI/control callback.
- Exposes global formatter selection/state variables `szDisc` and `bChanger`.
- Declares formatter drive acquisition, release, and query helpers.
- Provides `FmtAcquireDriveW` as a direct cast to the ANSI `FmtAcquireDrive()` implementation.

Dependencies:
- Requires prior definitions of `JS_DEVICE_TYPE`, Win32 `HWND`, `HANDLE`, `BOOL`, `PCHAR`, and related Windows/UDF formatter types.
- Implemented by `format_common.cpp`.

Notable risks:
- `FmtAcquireDriveW` is only a pointer cast rather than a true wide-character implementation; callers must pass compatible drive-string storage.
- The header has no include guard of its own in the visible content, so it relies on surrounding include discipline or being included idempotently through build structure.

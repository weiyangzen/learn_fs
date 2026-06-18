# File Research: sources/windows/reactos/drivers/filesystems/udfs/Include/user_lib.h

## Purpose
Declares the user-mode utility API implemented by `user_lib.cpp`.

## Main Contents
- Defines `ODS` debug-output macro and `arraylen`.
- Defines optical media/device enum `JS_DEVICE_TYPE`.
- Declares `MediaTypeStrings`.
- Defines `JS_SERVICE_STATE`.
- Declares CRT-like helpers, message box wrapper, registry wrappers, service/filter helpers, privilege/WOW64/event helpers, IOCTL/device-name helpers, option helpers, volume-open helper, drive-letter conversion, and `LauncherRoutine2`.
- Defines option lookup depth constants:
  - `UDF_OPTION_GLOBAL`
  - `UDF_OPTION_MEDIASPEC`
  - `UDF_OPTION_DEVSPEC`
  - `UDF_OPTION_DISKSPEC`
  - `UDF_OPTION_MAX_DEPTH`

## Dependencies and Interactions
- Assumes Windows-style types are already available: `PCHAR`, `ULONG`, `HANDLE`, `HINSTANCE`, `HWND`, `LPCSTR`, `LPCTSTR`, `LPTSTR`, `WCHAR`, and related Win32 declarations.
- Used by user-mode UDF utilities that need shared registry, service, and device-control behavior.

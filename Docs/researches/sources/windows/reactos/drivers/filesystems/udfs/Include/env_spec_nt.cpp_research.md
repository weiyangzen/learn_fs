# File Research: sources/windows/reactos/drivers/filesystems/udfs/Include/env_spec_nt.cpp

## Purpose

`env_spec_nt.cpp` implements NT-native-mode wrappers that emulate a subset of Win32-style APIs on top of NT system calls. It is compiled only under `NT_NATIVE_MODE`.

## Main Functions

- `GetOsVersion`
  - Reads `CurrentVersion` and `CurrentBuildNumber` from the Windows NT registry path.
  - Fills optional major, minor, and build outputs.
- `MyDeviceIoControl`
  - Routes control codes to `NtDeviceIoControlFile` or `NtFsControlFile` based on device type.
  - Waits for pending completion and reports returned byte count.
- `Sleep`
  - Implements millisecond sleep via `NtDelayExecution`.
- `MyGlobalAlloc` / `MyGlobalFree`
  - Lazily creates an RTL heap and allocates/frees from it.
- `PrintNtConsole`
  - Formats an ANSI debug message, prefixes line starts, converts to Unicode, and calls `NtDisplayString`.
- File wrappers:
  - `EnvFileOpenW`
  - `EnvFileOpenA`
  - `EnvFileClose`
  - `EnvFileGetSizeByHandle`
  - `EnvFileGetSizeA`
  - `EnvFileGetSizeW`
  - `EnvFileExistsA`
  - `EnvFileExistsW`
  - `EnvFileWrite`
  - `EnvFileRead`
  - `EnvFileSetPointer`
  - `EnvFileDeleteW`

## Integration Notes

This file pairs with `env_spec_nt.h`, which maps Win32-like names such as `DeviceIoControl`, `Sleep`, `GlobalAlloc`, and `ExitProcess` to these NT-native implementations.

## Risks And Edge Cases

- `GetOsVersion` parses the major/minor version as hexadecimal-style accumulation (`*16`) instead of decimal, which may be intentional for version IDs but is unusual.
- `MyDeviceIoControl` writes `*lpBytesReturned` without checking for null on success or warning paths.
- `EnvFileSetPointer` returns the existing `Status` when the computed position is negative; that value may be stale from a previous branch.
- `PrintNtConsole` uses static buffers and a global `was_enter`, so it is not thread-safe.
- `EnvFileOpenW` always requests read/write/synchronize access, so it is not suitable for read-only opens.

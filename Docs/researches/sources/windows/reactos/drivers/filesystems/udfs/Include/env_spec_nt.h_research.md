# File Research: sources/windows/reactos/drivers/filesystems/udfs/Include/env_spec_nt.h

## Purpose

`env_spec_nt.h` declares the NT-native environment abstraction and maps selected Win32-like APIs to NT-native helper implementations when `NT_NATIVE_MODE` is defined.

## Main Contents

- Includes `zw_2_nt.h` under `NT_NATIVE_MODE`.
- Defines `MAX_PATH` if missing.
- Declares `GetOsVersion` and maps `PsGetVersion` to it.
- Provides simple inline/macro versions of interlocked increment, decrement, and exchange-add.
- Maps `DeviceIoControl` to `MyDeviceIoControl`.
- Maps character conversion helpers to `swprintf`-based conversions.
- Declares `Sleep`.
- Maps `GlobalAlloc`/`GlobalFree` to `MyGlobalAlloc`/`MyGlobalFree`.
- Maps `ExitProcess` to `NtTerminateProcess`.
- Declares console and file helper functions:
  - `PrintNtConsole`
  - `EnvFileOpenW/A`
  - `EnvFileClose`
  - `EnvFileGetSizeByHandle`
  - `EnvFileGetSizeA/W`
  - `EnvFileExistsA/W`
  - `EnvFileWrite`
  - `EnvFileRead`
  - `EnvFileSetPointer`
  - `EnvFileDeleteW`
- Defines file seek mode constants:
  - `ENV_FILE_CURRENT`
  - `ENV_FILE_END`
  - `ENV_FILE_BEGIN`
- Maps `PrintDbgConsole` to `PrintNtConsole`.

## Integration Notes

This header allows shared formatter/tools code to compile in NT native mode without including Win32 user-mode APIs.

## Risks And Edge Cases

- The interlocked macros are not atomic; they are only safe in single-threaded or otherwise serialized native-mode utility contexts.
- `OemToCharW` and `MultiByteToWideChar` mappings ignore code page semantics and buffer size correctness.
- Macro replacements for common APIs can affect included code unexpectedly.

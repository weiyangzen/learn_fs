# File Research: sources/windows/reactos/drivers/filesystems/udfs/Include/regtools.cpp

## Purpose
Provides registry helper routines usable in both kernel and Win32 builds.

## Main Responsibilities
- `RegTGetKeyHandle` opens a registry key using `ZwOpenKey` in kernel mode or `RegOpenKeyExW` in Win32 mode.
- `RegTCloseKeyHandle` closes the corresponding handle with `ZwClose` or `RegCloseKey`.
- `RegTGetDwordValue` reads a DWORD value from a root/path/name tuple.
- `RegTGetStringValue` reads a Unicode string value, zeroes the destination first, and attempts null termination.

## Build Modes
- Non-`WIN_32_MODE` uses NT native registry APIs, `OBJECT_ATTRIBUTES`, `UNICODE_STRING`, and pool allocation for `KEY_VALUE_PARTIAL_INFORMATION`.
- `WIN_32_MODE` defaults null roots to `HKEY_LOCAL_MACHINE` and uses Win32 registry APIs.

## Notable Risks
- Win32 string termination checks `pStr[len-1]` even though `len` is byte count from `RegQueryValueExW`, which is easy to misuse for WCHAR indexing.
- Kernel string copy clamps byte count to `MaxLen`, so callers must pass byte capacity, not character capacity.

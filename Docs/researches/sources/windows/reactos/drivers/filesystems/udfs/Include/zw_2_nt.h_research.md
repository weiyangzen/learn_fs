# File Research: sources/windows/reactos/drivers/filesystems/udfs/Include/zw_2_nt.h

## Purpose
Small compatibility header that maps selected `Zw*` native calls to `Nt*` names when building in `NT_NATIVE_MODE`.

## Main Contents
- Include guard `__Zw_to_Nt__NameConvert__H__`.
- Under `NT_NATIVE_MODE`, defines:
  - `ZwClose` as `NtClose`
  - `ZwOpenKey` as `NtOpenKey`
  - `ZwQueryValueKey` as `NtQueryValueKey`
- Contains commented-out pool allocation macro substitutions.

## Dependencies and Interactions
- Used where the same code may target kernel-style `Zw*` APIs or native-mode `Nt*` APIs.

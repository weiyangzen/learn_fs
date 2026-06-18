# File Research: sources/windows/winbtrfs/src/mkbtrfs/resource.h

## Purpose

`resource.h` assigns numeric resource IDs for strings used by the `mkbtrfs` resource script and loaded at runtime by `mkbtrfs.c`.

## Defined IDs

- `IDS_USAGE` through `IDS_INVALID_CSUM_TYPE`, values 101 through 116.
- IDs cover usage text, conversion errors, drive recognition, DLL/function lookup failures, format result messages, argument errors, and checksum validation messages.

## Build Tool Metadata

The file includes standard Visual C++ resource-editor defaults under `APSTUDIO_INVOKED`:

- `_APS_NEXT_RESOURCE_VALUE`
- `_APS_NEXT_COMMAND_VALUE`
- `_APS_NEXT_CONTROL_VALUE`
- `_APS_NEXT_SYMED_VALUE`

## Dependencies

- Used by `mkbtrfs.rc.in`.
- Referenced by `mkbtrfs.c` through `print_string()` calls.

## Research Notes

- This is a coordination header: no executable logic, but changes can break resource lookup if not mirrored in the RC string table and C source references.

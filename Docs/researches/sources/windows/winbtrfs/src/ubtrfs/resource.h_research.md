# File Research: sources/windows/winbtrfs/src/ubtrfs/resource.h

## Purpose

`ubtrfs/resource.h` is the Visual Studio resource-editor header for the user-mode `ubtrfs` utility DLL resources. It contains no runtime filesystem logic.

## Contents

The file has the standard `//{{NO_DEPENDENCIES}}` generated header comments and AP Studio default ID definitions guarded by `APSTUDIO_INVOKED` and `APSTUDIO_READONLY_SYMBOLS`.

Defined defaults:

- `_APS_NEXT_RESOURCE_VALUE` = `101`
- `_APS_NEXT_COMMAND_VALUE` = `40001`
- `_APS_NEXT_CONTROL_VALUE` = `1001`
- `_APS_NEXT_SYMED_VALUE` = `101`

## Dependencies and Cross-File Interactions

`ubtrfs.rc.in` includes this header through the CMake-substituted path `@CMAKE_CURRENT_SOURCE_DIR@/src/ubtrfs/resource.h`. The current resource script only uses it as a conventional resource include; no symbolic resource IDs from this header are referenced elsewhere in the read file.

## Research Notes

This file is build/resource metadata only. Changes here matter for resource-editor generated IDs, not Btrfs format behavior.

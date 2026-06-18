# File Research: sources/windows/winbtrfs/src/btrfs.rc.in

## Role

`btrfs.rc.in` is a CMake-configured Windows resource script template for the WinBtrfs kernel driver binary, `btrfs.sys`.

## Contents

- Includes `@CMAKE_CURRENT_SOURCE_DIR@/src/resource.h` and Windows resource definitions through `<winresrc.h>`.
- Declares English (United Kingdom) resources with code page 1252.
- Provides Visual Studio `TEXTINCLUDE` blocks when `APSTUDIO_INVOKED` is set.
- Defines a `VS_VERSION_INFO` resource with `FILEVERSION` and `PRODUCTVERSION` substituted from `@PROJECT_VERSION_MAJOR@`, `@PROJECT_VERSION_MINOR@`, and `@PROJECT_VERSION_PATCH@`.
- Sets `FILEFLAGS` to debug when `_DEBUG` is defined, otherwise zero.
- Marks `FILEOS` as Win32, `FILETYPE` as application-like value `0x1L`, and subtype zero.
- Populates string metadata:
  - `FileDescription`: `WinBtrfs`
  - `FileVersion`: configured project version
  - `InternalName`: `btrfs`
  - `LegalCopyright`: `Copyright (c) Mark Harmstone 2016-24`
  - `OriginalFilename`: `btrfs.sys`
  - `ProductName`: `WinBtrfs`
  - `ProductVersion`: configured project version
- Adds `VarFileInfo` translation `0x809, 1200`, matching English UK and Unicode code page.

## Consumers

- Used by the WinBtrfs CMake build to generate the final `.rc` resource file embedded in the driver binary.
- Depends on `resource.h` for resource identifiers even though this template only defines version metadata directly.

## Notes

- This file contains no driver logic; its importance is release/build identity and version stamping.
- The `.in` suffix indicates CMake variable substitution is required before Windows resource compilation.

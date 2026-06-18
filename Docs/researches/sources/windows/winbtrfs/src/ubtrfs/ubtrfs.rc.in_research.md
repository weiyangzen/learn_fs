# File Research: sources/windows/winbtrfs/src/ubtrfs/ubtrfs.rc.in

## Purpose

`ubtrfs.rc.in` is the CMake-templated Windows resource script for `ubtrfs.dll`. It supplies version metadata embedded in the user-mode Btrfs utility DLL.

## Contents

The script includes `src/ubtrfs/resource.h` via `@CMAKE_CURRENT_SOURCE_DIR@`, includes `winresrc.h`, sets English (United Kingdom) resources with code page 1252, and defines AP Studio `TEXTINCLUDE` blocks for resource-editor compatibility.

The `VS_VERSION_INFO` block uses CMake substitutions for:

- `FILEVERSION @PROJECT_VERSION_MAJOR@,@PROJECT_VERSION_MINOR@,@PROJECT_VERSION_PATCH@,0`
- `PRODUCTVERSION @PROJECT_VERSION_MAJOR@,@PROJECT_VERSION_MINOR@,@PROJECT_VERSION_PATCH@,0`
- string `FileVersion`
- string `ProductVersion`

String metadata identifies the file as:

- `FileDescription`: `Btrfs utility DLL`
- `InternalName`: `ubtrfs`
- `OriginalFilename`: `ubtrfs.dll`
- `ProductName`: `WinBtrfs`
- `LegalCopyright`: `Copyright (c) Mark Harmstone 2016-24`

Debug builds set `FILEFLAGS 0x1L`; non-debug builds set `0x0L`. The resource declares `FILEOS 0x4L`, `FILETYPE 0x2L`, and translation `0x809, 1200`.

## Dependencies and Cross-File Interactions

This template is consumed by the build system to generate a `.rc` file with project version numbers substituted. It complements `ubtrfs.c` by branding/versioning the DLL but has no direct code dependency on formatting behavior.

## Research Notes

This is build metadata. Functional changes to filesystem formatting happen in `ubtrfs.c`; changes here affect Windows file properties and resource/version output.

# File Research: sources/windows/winbtrfs/src/mkbtrfs/mkbtrfs.rc.in

## Purpose

`mkbtrfs.rc.in` is the CMake-templated Windows resource script for `mkbtrfs.exe`. It provides version metadata and localized strings used by the formatting utility.

## Resource Content

- Includes `resource.h` through a CMake-expanded path.
- Includes `winresrc.h`.
- Defines English (United Kingdom) resources with code page 1252.
- Defines `VS_VERSION_INFO` with CMake project version substitutions:
  - `FILEVERSION`
  - `PRODUCTVERSION`
  - `FileVersion`
  - `ProductVersion`
- Version strings identify:
  - file description: Btrfs formatting utility,
  - internal name: `mkbtrfs`,
  - original filename: `mkbtrfs.exe`,
  - product name: WinBtrfs,
  - copyright range through 2024.

## String Table

Defines user-facing strings consumed by `mkbtrfs.c`, including:

- usage header and extended help text,
- multibyte conversion errors,
- invalid drive recognition,
- DLL/function loading failures,
- format failure and success messages,
- invalid or missing argument messages,
- checksum option validation messages.

The long `IDS_USAGE2` string documents device path syntax and all supported formatting flags.

## Dependencies

- `sources/windows/winbtrfs/src/mkbtrfs/resource.h` for numeric IDs.
- CMake variables:
  - `@CMAKE_CURRENT_SOURCE_DIR@`
  - `@PROJECT_VERSION_MAJOR@`
  - `@PROJECT_VERSION_MINOR@`
  - `@PROJECT_VERSION_PATCH@`

## Research Notes

- This file is build-time templated, not a final checked-in `.rc`.
- String IDs match the usage in `mkbtrfs.c`; changes here must stay synchronized with `resource.h`.
- The embedded help text is the authoritative CLI documentation for the standalone formatter.

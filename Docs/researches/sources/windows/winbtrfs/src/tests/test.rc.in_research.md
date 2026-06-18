# File Research: sources/windows/winbtrfs/src/tests/test.rc.in

## Purpose

`test.rc.in` is the CMake-configured Windows resource script template for the WinBtrfs test executable. It embeds version metadata and the executable manifest into `test.exe`.

## Main Contents

- Includes `winresrc.h` behind `APSTUDIO_READONLY_SYMBOLS`.
- Selects English (United Kingdom) resources:
  - `LANG_ENGLISH`
  - `SUBLANG_ENGLISH_UK`
  - code page `1252`
- Defines a `VS_VERSION_INFO` block with:
  - `FILEVERSION` and `PRODUCTVERSION` from `@PROJECT_VERSION_MAJOR@`, `@PROJECT_VERSION_MINOR@`, and `@PROJECT_VERSION_PATCH@`
  - debug flag set when `_DEBUG` is defined
  - `FILEOS 0x4L`, `FILETYPE 0x1L`, executable subtype zero
- Defines string metadata:
  - file description: `WinBtrfs test program`
  - internal name: `test`
  - original filename: `test.exe`
  - product name: `WinBtrfs`
  - copyright: Mark Harmstone 2021-24
- Defines `VarFileInfo` translation `0x809, 1200`.
- Embeds manifest resource `1 RT_MANIFEST "@CMAKE_CURRENT_SOURCE_DIR@/src/tests/manifest.xml"`.

## Integration

CMake substitutes the `@...@` project version and source-directory variables before compiling the resource. The resulting resource identifies the test binary consistently with WinBtrfs versioning and ensures the test executable carries its manifest.

## Notable Details

- This file contains no test logic.
- It is Windows-build metadata only.
- The manifest path is source-tree-relative through CMake substitution, so builds depend on `src/tests/manifest.xml` being present.

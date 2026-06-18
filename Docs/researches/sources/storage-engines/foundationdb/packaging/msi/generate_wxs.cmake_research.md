<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/packaging/msi/generate_wxs.cmake -->
# Research: sources/storage-engines/foundationdb/packaging/msi/generate_wxs.cmake

## Purpose
Small CMake script that normalizes configured paths for Windows and renders the WiX template.

## Important APIs, Types, And Functions
Uses `string(REPLACE ...)` to convert slashes to backslashes, derives `fdbc_lib` by replacing `dll` with `lib`, prints a status line, and calls `configure_file(... @ONLY NEWLINE_STYLE DOS)`.

## Control Flow
Called by the MSI CMake custom command with `-D` variables, transforms path variables, then writes the generated `.wxs` file.

## State And Persistence Behavior
Writes only the configured WiX XML output path supplied as `OUT`.

## Dependencies And Integration Points
Depends on CMake variable injection from `packaging/msi/CMakeLists.txt` and the `.wxs.cmake` input. Bridges portable CMake build paths to WiX/Windows path syntax.

## Risks And Edge Cases
The simple `dll` to `lib` replacement can affect unexpected substrings if paths contain `dll` elsewhere. Missing variables become empty strings and may create a syntactically valid but unusable installer.

## Test Signals
Validated by successful generation and WiX compilation in the `installer` target.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/packaging/msi/generate_wxs.cmake -->

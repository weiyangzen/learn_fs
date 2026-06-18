# sources/storage-engines/foundationdb/cmake/FindWIX.cmake

## Purpose
Locates WiX Toolset executables for Windows installer generation.

## Important APIs, Types, and Functions
Finds `WIX_CANDLE` and `WIX_LIGHT` under `$WIX/bin` or PATH and reports via `find_package_handle_standard_args`.

## Control Flow and Integration
Windows packaging code can require this module before building MSI artifacts.

## State and Persistence
Depends on WiX environment variable/path and CMake package handle standard args.

## Dependencies
No generated state; only CMake variables.

## Risks and Test Signals
Risks include the script appearing to miss a closing parenthesis in the checked source, which would break inclusion unless patched elsewhere. Test signal is successful CMake parsing and WiX executable discovery.

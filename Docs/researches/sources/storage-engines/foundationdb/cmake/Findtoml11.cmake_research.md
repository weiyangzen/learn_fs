# sources/storage-engines/foundationdb/cmake/Findtoml11.cmake

## Purpose
Finds an installed toml11 header-only library and exposes CMake variables.

## Important APIs, Types, and Functions
Searches `toml11_INCLUDE_DIRS`, reads version macros from toml11 headers when available, and reports `toml11_FOUND`/`toml11_VERSION`.

## Control Flow and Integration
`FDBComponents.cmake` first tries config-mode `find_package(toml11 3.8.1 EXACT QUIET CONFIG)` and uses FetchContent fallback, while this module supports manual root-based discovery where requested.

## State and Persistence
Depends on `toml11_ROOT` and toml11 include layout/version defines.

## Dependencies
No generated state; variables are advanced.

## Risks and Test Signals
Risks include duplicate discovery paths between config mode and this module. Test signal is `toml11::toml11` availability for C++ code.

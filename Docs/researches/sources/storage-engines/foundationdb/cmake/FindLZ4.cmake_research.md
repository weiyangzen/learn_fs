# sources/storage-engines/foundationdb/cmake/FindLZ4.cmake

## Purpose
Finds LZ4 headers/library and exposes imported target `LZ4::LZ4`.

## Important APIs, Types, and Functions
Searches `LZ4_INCLUDE_DIR`, `LZ4_LIBRARY`, parses version macros from `lz4.h`, and sets `LZ4_INCLUDE_DIRS`, `LZ4_LIBRARIES`, `LZ4_VERSION`.

## Control Flow and Integration
Used by RocksDB-enabled fdbserver builds before `CompileRocksDB.cmake`; if found, downstream code links the imported target or variables.

## State and Persistence
Depends on `LZ4_ROOT` or environment root, `FindPackageHandleStandardArgs`, and `lz4.h` version macros.

## Dependencies
No generated state; CMake cache variables and imported target properties persist.

## Risks and Test Signals
Risks include regex parsing across LZ4 header changes and library/header version mismatch. Test signal is required `find_package(LZ4)` success and RocksDB/FDB link.

# sources/storage-engines/rocksdb/cmake/modules/Findlz4.cmake

## Purpose
Finds the LZ4 compression dependency and provides a target named `lz4::lz4`.

## Important APIs and Control Flow
The module locates `lz4.h` using `${lz4_ROOT_DIR}/include`, locates library `lz4` using `${lz4_ROOT_DIR}/lib`, and calls `find_package_handle_standard_args(lz4 ...)`. When `lz4_FOUND` is true and the target is absent, it creates an UNKNOWN IMPORTED target with `IMPORTED_LOCATION` and `INTERFACE_INCLUDE_DIRECTORIES`.

## Dependencies, Risks, and Test Signals
It participates in `WITH_LZ4` CMake builds and installed package dependency discovery. Risks include no version checking and lowercase package variable/target naming that must match the rest of the build. Functional test signal comes from LZ4-dependent tests such as tiered secondary cache tests.

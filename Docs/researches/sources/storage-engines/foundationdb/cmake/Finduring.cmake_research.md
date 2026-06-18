# sources/storage-engines/foundationdb/cmake/Finduring.cmake

## Purpose
Finds liburing headers and library for optional RocksDB/io_uring support.

## Important APIs, Types, and Functions
Sets `uring_INCLUDE_DIR`, `uring_LIBRARY`, `uring_FOUND`, and creates imported target `uring::uring` when found.

## Control Flow and Integration
RocksDB-enabled fdbserver configuration may require this module when `WITH_LIBURING` is enabled.

## State and Persistence
Depends on liburing install paths and `FindPackageHandleStandardArgs`.

## Dependencies
No generated files; imported target state persists in CMake.

## Risks and Test Signals
Risks include no version validation and target availability only when both header/library are found. Test signal is RocksDB build with `-DWITH_LIBURING=ON` linking successfully.

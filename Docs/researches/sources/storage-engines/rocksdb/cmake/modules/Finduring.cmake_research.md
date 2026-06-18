# sources/storage-engines/rocksdb/cmake/modules/Finduring.cmake

## Purpose
Finds liburing for optional io_uring support and exports an imported target.

## Important APIs and Control Flow
The module searches for `liburing.h` and library names `liburing.a` or `liburing`. `find_package_handle_standard_args(uring ...)` sets `uring_FOUND`. On success, it creates `uring::uring` as an UNKNOWN IMPORTED target with include directories, C link-interface language, and imported location.

## Dependencies, Risks, and Test Signals
No runtime state is persisted; only CMake variables and target definitions are produced. Risks include preferring a static archive when both static and shared libraries exist, no version checks for io_uring feature availability, and Linux-specific assumptions. Build/test coverage comes from io_uring-enabled RocksDB configurations.

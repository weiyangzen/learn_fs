# sources/storage-engines/rocksdb/third-party/gtest-1.8.1/fused-src/gtest/CMakeLists.txt

Purpose: minimal CMake build file for the vendored fused GoogleTest source.

Important APIs/control flow: `add_library(gtest gtest-all.cc)` builds a `gtest` library target from the fused source. `target_link_libraries(gtest ${CMAKE_THREAD_LIBS_INIT})` links the thread library selected by the parent CMake configuration.

State and persistence: no runtime state and no generated configuration beyond the build target.

Dependencies/integration: assumes `gtest-all.cc` is present in the same fused source directory and that `${CMAKE_THREAD_LIBS_INIT}` has been set by a parent `find_package(Threads)` or equivalent.

Risks and test signals: this file does not set include directories, compile options, or thread discovery itself, so it relies on surrounding RocksDB CMake configuration. Build tests should verify vendored gtest target creation and successful link on platforms requiring explicit pthread/thread libraries.

# sources/storage-engines/foundationdb/cmake/FindThreads.cmake

## Purpose
Custom thread discovery module based on CMake's FindThreads with FoundationDB Swift-aware pthread handling.

## Important APIs, Types, and Functions
Defines internal macros `_threads_check_libc`, `_threads_check_lib`, `_threads_check_flag_pthread`; sets `CMAKE_THREAD_LIBS_INIT`, `CMAKE_USE_PTHREADS_INIT`, `Threads_FOUND`; creates `Threads::Threads`.

## Control Flow and Integration
The module compiles a pthread test, optionally tries `-pthread` first, checks pthread libraries, handles Windows/HP-UX/Cygwin cases, and assigns generator expressions so Swift links use `-lpthread` while non-Swift C/C++ uses `-pthread`.

## State and Persistence
Depends on `CheckForPthreads.c`, C/C++ compiler availability, pthread headers/libraries, and CMake check modules.

## Dependencies
State is cached check results and imported target compile/link properties; try-compile output may be appended to `CMakeError.log`.

## Risks and Test Signals
Risks include the custom Swift generator expressions diverging from upstream CMake, cross-language link behavior, and cached check results after toolchain changes. Test signals are `find_package(Threads REQUIRED)` success and Swift/C++ linked binaries.

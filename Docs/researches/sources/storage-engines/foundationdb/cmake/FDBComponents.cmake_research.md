# sources/storage-engines/foundationdb/cmake/FDBComponents.cmake

## Purpose
Discovers and gates optional FoundationDB components and language bindings.

## Important APIs, Types, and Functions
Sets component flags for jemalloc, valgrind, OpenSSL/ZLIB, Swift, Python/C/Java/Go/Ruby bindings, documentation, mako, RocksDB, toml11, coroutine implementation, AWS backup, gRPC, and `packages`; defines `print_components`.

## Control Flow and Integration
The module resolves dependencies in order: low-level alloc/profiling, crypto/compression, language runtimes, binding prerequisites, external libraries, and package directory setup. Options and found tools decide `WITH_*` flags, and `FORCE_ALL_COMPONENTS` can turn missing optional dependencies into configure errors.

## State and Persistence
Depends on many custom find/compile modules, Python/JNI/Java/Go/Ruby/Swift tools, OpenSSL/ZLIB, RocksDB, protobuf/gRPC/absl, and external network sources.

## Dependencies
State is mostly CMake cache/options and global `WITH_*` variables; it may also FetchContent toml11 or Swift bindings into the source tree when absent.

## Risks and Test Signals
Risks include hidden downloads, binding flags depending on earlier C binding/Python decisions, sanitizer disabling Go/Swift, and version checks for protoc/Swift. Test signals are component overview output and successful builds of selected bindings/packages.

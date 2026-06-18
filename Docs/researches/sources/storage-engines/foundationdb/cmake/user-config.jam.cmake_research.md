# sources/storage-engines/foundationdb/cmake/user-config.jam.cmake

## Purpose
Boost.Build user-config template generated for source-built Boost.

## Important APIs, Types, and Functions
Contains `using <toolset>` with compiler and additional options, plus zstd include/search configuration.

## Control Flow and Integration
`CompileBoost.cmake` configures this into the build tree and passes it to b2 via `--user-config` so Boost uses the same compiler/linker settings as FoundationDB.

## State and Persistence
Depends on `BOOST_TOOLSET`, `BOOST_CXX_COMPILER`, `BOOST_ADDITIONAL_COMPILE_OPTIONS`, and `CMAKE_BINARY_DIR` substitutions.

## Dependencies
Configured `user-config.jam` persists in the CMake binary directory.

## Risks and Test Signals
Risks include stale options after reconfiguring toolchains and zstd version/path assumptions. Test signal is successful Boost ExternalProject build.

# sources/storage-engines/foundationdb/cmake/benchmark-download.cmake

## Purpose
ExternalProject bootstrap project used by `FDBBenchmark.cmake` to download Google Benchmark and Googletest sources.

## Important APIs, Types, and Functions
Declares `googlebenchmark` and dependent `googletest` ExternalProjects with pinned commits and shallow clones.

## Control Flow and Integration
`FDBBenchmark.cmake` copies this file as a standalone CMakeLists, configures/builds it, then adds the downloaded benchmark source directory to the main build.

## State and Persistence
Depends on Git, GitHub availability, and the pinned benchmark/googletest commits.

## Dependencies
State is downloaded source/build trees under `googlebenchmark-download`.

## Risks and Test Signals
Risks include no hash verification for git clones and old dependency versions. Test signal is populated `googlebenchmark-src` with googletest before benchmark target configuration.

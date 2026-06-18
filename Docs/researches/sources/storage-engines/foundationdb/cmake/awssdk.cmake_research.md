# sources/storage-engines/foundationdb/cmake/awssdk.cmake

## Purpose
Builds a static AWS SDK C++ core dependency bundle for FoundationDB S3 backup support.

## Important APIs, Types, and Functions
Defines ExternalProject `awssdk_project`, imported static targets for AWS core/CRT/C libraries, curl, zlib, and interface target `awssdk_target`.

## Control Flow and Integration
The module checks libc++ compiler flags, fetches a pinned AWS SDK commit, builds only core with static libs, BYO crypto, curl, and zlib, then wires a long dependency-ordered link list into `awssdk_target`.

## State and Persistence
Depends on GitHub aws-sdk-cpp, CMake ExternalProject, current C++ compiler, curl/zlib produced by the AWS build, and static library paths under `lib64`/external install.

## Dependencies
State persists in `awssdk-src`, `awssdk-build`, installed static libraries, and imported target properties.

## Risks and Test Signals
Risks include dependency order fragility, ABI mismatch when compiler/libc++ flags are incomplete, large external build cost, and hard-coded library paths. Test signal is successful `BUILD_AWS_BACKUP` link and S3 backup tests.

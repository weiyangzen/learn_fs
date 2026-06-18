# sources/storage-engines/foundationdb/contrib/folly_memcpy/CMakeLists.txt

## Purpose
Conditionally builds the optimized Folly-derived memcpy assembly library on Unix non-Apple platforms.

## Important APIs, Types, And Functions
When `UNIX AND NOT APPLE`, adds static library `folly_memcpy` from `folly_memcpy.S` and publishes the current directory for `folly_memcpy.h`.

## Control Flow
CMake condition gates target creation by platform.

## State And Persistence
No runtime state. It controls whether the library exists in the build graph.

## Dependencies And Integration
Works with the assembly file's own x86_64 Linux guard and header declarations. Consumers include `folly_memcpy.h`.

## Risks
CMake permits FreeBSD by condition, while the assembly emits code only for `__x86_64__ && __linux__ && !__CYGWIN__`; this can create an empty or unusable archive on some Unix non-Apple platforms. Header declaration requires `__AVX__`, but CMake does not gate target creation on AVX.

## Test Signals
Configure/build on Linux x86_64 with AVX, Linux without AVX, FreeBSD, and macOS to confirm intended target availability.

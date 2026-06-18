# sources/storage-engines/wiredtiger/cmake/platform/os/darwin.cmake

## Purpose
`darwin.cmake` applies macOS-specific WiredTiger build settings.

## Important APIs, Types, And Functions
It sets `WT_POSIX ON`, disables `ENABLE_CPPSUITE`, and adds `${CMAKE_SOURCE_DIR}/oss/apple` as a system include directory.

## Control Flow
There is no branching. macOS builds are treated as POSIX, exclude cppsuite, and include Apple portability headers.

## State And Persistence Behavior
It writes cache values and include-directory state that persist for the build directory.

## Dependencies And Integration Points
It integrates with POSIX feature config, build option dependency evaluation, and portable futex headers under `oss/apple`.

## Risks
Disabling cppsuite here can hide macOS regressions in C++ test coverage. The system include path can mask warnings from portability shims.

## Test Signals
Configure and build on macOS; verify POSIX code paths, futex shim includes, and absence of cppsuite targets.

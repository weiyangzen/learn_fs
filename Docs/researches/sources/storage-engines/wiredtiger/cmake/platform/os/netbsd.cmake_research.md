# sources/storage-engines/wiredtiger/cmake/platform/os/netbsd.cmake

## Purpose
`netbsd.cmake` marks NetBSD as a POSIX WiredTiger platform.

## Important APIs, Types, And Functions
It sets `WT_POSIX ON` in the CMake cache.

## Control Flow
There is no branching or additional setup.

## State And Persistence Behavior
The POSIX cache flag persists for the build directory and affects option dependencies and install/pkg-config behavior.

## Dependencies And Integration Points
It integrates with generated POSIX feature macros in `wiredtiger_config.h.in` and general POSIX build paths.

## Risks
The minimal file assumes no NetBSD-specific flags are required. If source code grows platform-specific needs, this file may under-configure the build.

## Test Signals
Configure and build on NetBSD, verifying POSIX feature macros and linked libraries.

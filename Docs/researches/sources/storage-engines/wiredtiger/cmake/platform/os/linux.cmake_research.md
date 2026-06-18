# sources/storage-engines/wiredtiger/cmake/platform/os/linux.cmake

## Purpose
`linux.cmake` applies Linux-specific WiredTiger build settings.

## Important APIs, Types, And Functions
It sets `WT_POSIX ON` and adds `_GNU_SOURCE` as a compile definition.

## Control Flow
There is no branching. Linux builds always expose POSIX configuration and GNU/Linux extension APIs.

## State And Persistence Behavior
The file persists `WT_POSIX` in the cache and adds a global compile definition for all targets configured after it.

## Dependencies And Integration Points
It enables Linux feature declarations used by source code, such as `pthread_setname_np`, and drives POSIX dependency options in `base.cmake`.

## Risks
Global `_GNU_SOURCE` can change libc header behavior and should stay consistent across all translation units. Missing it can cause compile failures for GNU extension use.

## Test Signals
Configure Linux builds and verify `_GNU_SOURCE` appears on compile lines and POSIX/Linux feature macros are set in generated config.

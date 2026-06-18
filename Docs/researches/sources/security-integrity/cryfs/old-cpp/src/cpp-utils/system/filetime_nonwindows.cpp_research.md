# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/system/filetime_nonwindows.cpp

## Purpose
Implements small platform abstraction helpers for disk space, environment variables, file times, memory locking, paths, stats, home directories, and clocks. This specific file has 39 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils/system` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Types/classes: `timeval`. Important declarations or call sites include `int set_filetime(const char *filepath, timespec lastAccessTime, timespec lastModificationTime) {`; `TIMESPEC_TO_TIMEVAL(&casted_times[0], &lastAccessTime);`; `TIMESPEC_TO_TIMEVAL(&casted_times[1], &lastModificationTime);`; `int retval = ::utimes(filepath, casted_times.data());`; `if (0 == retval) {`; `int get_filetime(const char *filepath, timespec* lastAccessTime, timespec* lastModificationTime) {`; `int retval = ::stat(filepath, &attrib);`; `if (retval != 0) {`. CMake commands used here include `TIMESPEC_TO_TIMEVAL`, `if`. Primary includes/dependencies visible in the file include `filetime.h`, `utime.h`, `sys/time.h`, `sys/stat.h`, `errno.h`, `array`, `cpp-utils/system/stat.h`.

## Control Flow
System helpers branch by platform or call Boost/POSIX/Win32 APIs, normalize the result into simple values, and throw or return optional-like results on unavailable platform data.

## State and Persistence Behavior
Most helpers are stateless wrappers around platform state. Memory-locking allocators affect virtual memory residency for the lifetime of the allocation.

## Dependencies and Integration Points
Integration is through the local cpp-utils/CryFS headers and external libraries named in the includes/build graph; visible includes are `filetime.h`, `utime.h`, `sys/time.h`, `sys/stat.h`, `errno.h`, `array`, `cpp-utils/system/stat.h`.

## Risks and Edge Cases
Platform helpers can differ subtly by OS, filesystem, or permissions; memory locking is best-effort and can fail or be limited by process privileges.

## Test Signals
Use platform-specific tests for disk space, env lookup, home directory, filetime conversion, memory locking failure paths, stat/path aliases, and monotonic/time helpers.
